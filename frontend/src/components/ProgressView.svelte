<script lang="ts">
  import { CalendarDays, Download, Filter, RotateCcw, Trophy, X } from "@lucide/svelte";
  import { onMount } from "svelte";
  import {
    downloadProgress, fetchExerciseHistory, fetchExercises, fetchOverview, fetchPrograms, fetchRecords,
    type AnalyticsQuery, type ExerciseHistory, type ExerciseInfo, type Formula, type PersonalRecord, type ProgramProgress, type TrainingOverview,
  } from "../api";
  import { formatDate, formatSplit } from "../format";
  import MetricChart, { type ChartPoint } from "./MetricChart.svelte";

  interface Props { onOpen: (id: string) => void; initialExercise?: string; refresh?: number }
  let { onOpen, initialExercise = "", refresh = 0 }: Props = $props();
  let exercises = $state<ExerciseInfo[]>([]);
  let programs = $state<ProgramProgress[]>([]);
  let showPrograms = $state(true);
  let appliedQuery = $state<AnalyticsQuery>();
  let exercise = $state("");
  let from = $state("");
  let to = $state("");
  let bucket = $state<"day" | "week" | "month">("week");
  let formula = $state<Formula>("epley");
  let loadKg = $state<number | undefined>(undefined);
  let recordScope = $state("all");
  type Metric = "estimated_one_rm_kg" | "best_load_kg" | "best_reps" | "volume_kg_reps" | "relative_strength" | "assistance_kg" | "hold_seconds" | "height_cm" | "sets_per_minute";
  let metric = $state<Metric>("estimated_one_rm_kg");
  const metricOptions: { id: Metric; label: string; unit: string }[] = [
    { id: "estimated_one_rm_kg", label: "Estimated 1RM", unit: "kg" },
    { id: "best_load_kg", label: "Best recorded load", unit: "kg" },
    { id: "best_reps", label: "Most repetitions", unit: "reps" },
    { id: "volume_kg_reps", label: "Known-load volume", unit: "kg-reps" },
    { id: "relative_strength", label: "Bodyweight-relative strength", unit: "ratio" },
    { id: "assistance_kg", label: "Assistance", unit: "kg" },
    { id: "hold_seconds", label: "Longest hold", unit: "seconds" },
    { id: "height_cm", label: "Highest jump", unit: "cm" },
    { id: "sets_per_minute", label: "Exercise sets / session minute", unit: "sets/min" },
  ];
  let overview = $state<TrainingOverview | null>(null);
  let history = $state<ExerciseHistory | null>(null);
  let records = $state<PersonalRecord[]>([]);
  let loading = $state(true);
  let error = $state("");
  let exporting = $state(false);
  let selectedIds = $state<string[]>([]);
  let calendarYear = $state("");
  let showAll = $state(false);
  let controller: AbortController | null = null;
  let mounted = false;
  const selectedMetric = $derived(metricOptions.find((item) => item.id === metric)!);
  const programBands = $derived(programs
    .filter((entry) => entry.program.start <= to && (!entry.program.end || entry.program.end >= from))
    .map((entry) => ({ name: entry.program.name, start: entry.program.start > from ? entry.program.start : from, end: entry.program.end && entry.program.end < to ? entry.program.end : to })));
  const exerciseChange = $derived(history?.comparison[metric === "best_load_kg" ? "load" : metric === "best_reps" ? "reps" : metric === "volume_kg_reps" ? "volume" : metric === "assistance_kg" ? "assistance" : "estimated_one_rm"]);
  const calendarYears = $derived([...new Set((overview?.activity || []).map((day) => day.date.slice(0, 4)))].sort());
  const calendarDays = $derived((overview?.activity || []).filter((day) => day.date.startsWith(calendarYear)));
  const calendarOffset = $derived(calendarDays.length ? (new Date(`${calendarDays[0].date}T12:00:00Z`).getUTCDay() + 6) % 7 : 0);
  const tableSessions = $derived(selectedIds.length ? (overview?.sessions || []).filter((session) => selectedIds.includes(session.workout_id)) : history?.sessions || []);
  const displayedSessions = $derived([...tableSessions].reverse().slice(0, showAll ? undefined : 25));

  onMount(() => {
    const parameters = new URLSearchParams(window.location.search);
    from = parameters.get("from") || "";
    to = parameters.get("to") || "";
    exercise = parameters.get("exercise") || initialExercise;
    if (parameters.has("load_kg")) loadKg = Number(parameters.get("load_kg"));
    const savedFormula = parameters.get("formula");
    if (savedFormula === "epley" || savedFormula === "brzycki" || savedFormula === "acsm") formula = savedFormula;
    void initialize().then(() => { mounted = true; });
    return () => { mounted = false; controller?.abort(); };
  });

  $effect(() => { void refresh; if (mounted) void load(); });

  function message(cause: unknown): string { return cause instanceof Error ? cause.message : "Progress data is unavailable"; }
  function number(value: number | null | undefined, digits = 1): string {
    return value == null ? "Not measured" : new Intl.NumberFormat("en-GB", { maximumFractionDigits: digits }).format(value);
  }
  function comparison(label: string): string {
    const value = overview?.comparison[label]?.percent;
    return value == null ? "No prior comparison" : `${value > 0 ? "+" : ""}${number(value)}% vs prior period`;
  }
  function recordLabel(value: string): string {
    return ({ load: "Load", reps: "Repetitions", estimated_one_rm: "Estimated 1RM", assistance: "Least assistance", hold: "Longest hold", height: "Highest jump" } as Record<string, string>)[value] || value;
  }
  async function initialize(): Promise<void> {
    controller?.abort();
    controller = new AbortController();
    try {
      [exercises, programs] = await Promise.all([fetchExercises(controller.signal), fetchPrograms(controller.signal)]);
      const dates = exercises.map((item) => item.last_date).sort();
      const latest = dates[dates.length - 1] || new Date().toISOString().slice(0, 10);
      from ||= `${latest.slice(0, 4)}-01-01`;
      to ||= latest;
      if (!exercises.some((item) => item.id === exercise)) exercise = exercises.find((item) => item.aliases.includes(exercise))?.id || exercises.find((item) => item.id === "bench_press")?.id || exercises[0]?.id || "";
      await load();
    } catch (cause) {
      if (!(cause instanceof DOMException && cause.name === "AbortError")) { error = message(cause); loading = false; }
    }
  }
  async function load(): Promise<void> {
    if (!from || !to || from > to) { error = "Choose an ordered date range"; return; }
    controller?.abort();
    const active = new AbortController();
    controller = active;
    loading = true; error = ""; selectedIds = []; showAll = false;
    try {
      const query = { from, to, bucket, formula };
      const [summary, progression, best] = await Promise.all([
        fetchOverview(query, active.signal),
        exercise ? fetchExerciseHistory(exercise, { ...query, load_kg: loadKg }, active.signal) : Promise.resolve(null),
        exercise ? fetchRecords({ exercise_id: exercise, formula, ...(recordScope === "period" ? { from, to } : {}) }, active.signal) : Promise.resolve([]),
      ]);
      if (active.signal.aborted) return;
      overview = summary; history = progression; records = best;
      appliedQuery = { from: query.from, to: query.to, formula: query.formula, exercise_id: progression?.exercise_id, load_kg: progression?.load_kg ?? loadKg };
      if (!calendarYear || !summary.activity.some((day) => day.date.startsWith(calendarYear))) calendarYear = to.slice(0, 4);
      const url = new URL(window.location.href);
      for (const [key, value] of Object.entries({ view: "progress", from, to, exercise, formula })) url.searchParams.set(key, value);
      if (loadKg === undefined) url.searchParams.delete("load_kg"); else url.searchParams.set("load_kg", String(loadKg));
      window.history.replaceState(null, "", url);
    } catch (cause) {
      if (!active.signal.aborted) error = message(cause);
    } finally { if (!active.signal.aborted) loading = false; }
  }
  function select(point: ChartPoint): void {
    const ids = point.workoutIds || [];
    if (ids.length === 1) onOpen(ids[0]);
    else { selectedIds = ids; showAll = true; }
  }
  function exercisePoints(): ChartPoint[] {
    return (history?.sessions || []).map((session) => ({ date: session.date, value: session[metric], workoutIds: [session.workout_id] }));
  }
  function preset(mode: "year" | "90" | "all"): void {
    if (!exercises.length) return;
    const latest = [...exercises.map((item) => item.last_date)].sort().slice(-1)[0];
    to = latest;
    if (mode === "year") from = `${latest.slice(0, 4)}-01-01`;
    else if (mode === "all") from = [...exercises.map((item) => item.first_date)].sort()[0];
    else { const beginning = new Date(`${latest}T12:00:00Z`); beginning.setUTCDate(beginning.getUTCDate() - 89); from = beginning.toISOString().slice(0, 10); }
    void load();
  }
  async function exportCsv(): Promise<void> {
    exporting = true;
    try { await downloadProgress(appliedQuery || { from, to, formula, exercise_id: exercise || undefined }); }
    catch (cause) { error = message(cause); }
    finally { exporting = false; }
  }
</script>

<section class="progress-view" aria-label="Training progress" aria-busy={loading}>
  <form class="analytics-controls" onsubmit={(event) => { event.preventDefault(); void load(); }}>
    <label>From<input aria-label="Progress start date" type="date" bind:value={from} required max={to || undefined} /></label>
    <label>To<input aria-label="Progress end date" type="date" bind:value={to} required min={from || undefined} /></label>
    <label class="exercise-filter">Exercise<select aria-label="Progress exercise" bind:value={exercise} onchange={() => void load()}>
      {#each exercises as item}<option value={item.id}>{item.label}</option>{/each}
    </select></label>
    <label>Bucket<select aria-label="Activity bucket" bind:value={bucket} onchange={() => void load()}><option value="day">Daily</option><option value="week">Weekly</option><option value="month">Monthly</option></select></label>
    <label>1RM formula<select aria-label="1RM formula" bind:value={formula} onchange={() => void load()}><option value="epley">Epley</option><option value="brzycki">Brzycki</option><option value="acsm">ACSM</option></select></label>
    <button class="primary-button" type="submit" disabled={loading}><Filter size={16} /> Apply</button>
    <button class="secondary-button" type="button" disabled={exporting || loading || !overview} onclick={() => void exportCsv()}><Download size={16} /> Export CSV</button>
  </form>
  <div class="range-presets"><button type="button" onclick={() => preset("year")}>Year to date</button><button type="button" onclick={() => preset("90")}>Last 90 days</button><button type="button" onclick={() => preset("all")}>All time</button></div>
  {#if error}<div class="inline-error" role="alert">{error}<button class="secondary-button" type="button" onclick={() => void initialize()}><RotateCcw size={16} /> Retry</button></div>{/if}
  {#if loading && !overview}<div class="loading-state" aria-live="polite"><span class="loading-bar"></span>Loading progress</div>{/if}
  {#if overview}
    <div class="progress-summary metric-strip">
      <div><span class="metric-value">{overview.workouts}</span><span class="metric-label">workouts<small>{comparison("workouts")}</small></span></div>
      <div><span class="metric-value">{number(overview.sets, 0)}</span><span class="metric-label">sets<small>{comparison("sets")}</small></span></div>
      <div><span class="metric-value">{number(overview.volume_kg_reps, 0)}</span><span class="metric-label">known kg-reps<small>{overview.known_load_sets} of {overview.sets} sets with known load</small></span></div>
      <div><span class="metric-value">{number(overview.duration_minutes, 0)}</span><span class="metric-label">training minutes<small>{overview.duration_workouts} of {overview.workouts} sessions timed</small></span></div>
    </div>
    <div class="section-heading"><h2>{formatSplit(exercise) || "Exercise progression"}</h2><div class="metric-controls"><label class="checkbox-label"><input type="checkbox" bind:checked={showPrograms} /> Program phases</label><label>Recorded total load (kg)<input aria-label="Compare at recorded load" type="number" min="0" max="5000" step="0.5" bind:value={loadKg} onchange={() => void load()} /></label><label>Metric<select aria-label="Progress metric" bind:value={metric} title={selectedMetric.label}>{#each metricOptions as item}<option value={item.id}>{item.label}</option>{/each}</select></label></div></div>
    <div class="chart-grid">
      <MetricChart title={selectedMetric.label} unit={selectedMetric.unit} series={[{ name: selectedMetric.label, points: exercisePoints() }]} bands={showPrograms ? programBands : []} onSelect={select} />
      <MetricChart title="Training activity" unit="workouts" kind="bar" series={[{ name: "Workouts", points: overview.buckets.map((item) => ({ date: item.date, value: item.workouts, workoutIds: item.workout_ids })) }]} onSelect={select} />
      <MetricChart title="Known-load volume" unit="kg-reps" kind="bar" series={[{ name: "Volume", points: overview.buckets.map((item) => ({ date: item.date, value: item.volume_kg_reps, workoutIds: item.workout_ids })) }]} onSelect={select} />
      <MetricChart title="Training duration" unit="minutes" series={[{ name: "Duration", points: overview.buckets.map((item) => ({ date: item.date, value: item.duration_minutes, workoutIds: item.workout_ids })) }]} onSelect={select} />
    </div>
    <div class="metric-context"><span>{history?.sessions.length || 0} exercise sessions</span><span>1RM eligibility: 1-10 reps, known external load</span><span>{overview.excluded_load_sets} sets with unavailable load</span></div>
    {#if exerciseChange?.delta != null && ["best_load_kg", "best_reps", "volume_kg_reps", "assistance_kg", "estimated_one_rm_kg"].includes(metric)}<p class="status-line">Last session: {number(exerciseChange.current)} {selectedMetric.unit}; previous: {number(exerciseChange.previous)} {selectedMetric.unit} ({exerciseChange.delta > 0 ? "+" : ""}{number(exerciseChange.delta)})</p>{/if}
    <section class="data-section" aria-label="Activity calendar">
      <div class="section-heading"><h2><CalendarDays size={21} /> Activity</h2><label>Year<select aria-label="Calendar year" bind:value={calendarYear}>{#each calendarYears as year}<option value={year}>{year}</option>{/each}</select></label></div>
      <div class="calendar-scroll"><div class="activity-calendar" role="grid" aria-label={`${calendarYear} training days`}>
        {#each Array(calendarOffset) as _}<span class="calendar-blank"></span>{/each}
        {#each calendarDays as day}<button type="button" role="gridcell" class="calendar-day" class:level-one={day.workouts === 1} class:level-two={day.workouts === 2} class:level-three={day.workouts >= 3} disabled={!day.workouts} title={`${formatDate(day.date)}: ${day.workouts} workouts`} aria-label={`${formatDate(day.date)}: ${day.workouts} workouts`} onclick={() => select({ date: day.date, value: day.workouts, workoutIds: day.workout_ids })}></button>{/each}
      </div></div>
      <div class="metric-context"><span>{overview.active_days} active days</span><span>Longest training gap: {number(overview.longest_gap_days, 0)} days</span></div>
    </section>
    <section class="data-section" aria-label="Personal records">
      <div class="section-heading"><h2><Trophy size={21} /> Personal records</h2><label>Period<select aria-label="Record period" bind:value={recordScope} onchange={() => void load()}><option value="all">All time</option><option value="period">Selected period</option></select></label></div>
      <div class="record-strip">{#each records as record}<button type="button" class="record-item" onclick={() => onOpen(record.workout_id)}><span>{recordLabel(record.metric)}</span><strong>{number(record.value)} <small>{record.unit}</small></strong><time datetime={record.date}>{formatDate(record.date)}</time></button>{/each}</div>
      {#if !records.length}<p class="empty-line">No records for this selection</p>{/if}
    </section>
    <div class="distribution-grid">
      <section class="data-section"><h3>Sets by muscle group</h3><div class="distribution-list">{#each Object.entries(overview.muscle_group_sets).sort((first, second) => second[1] - first[1]) as [group, count]}<div><span>{formatSplit(group)}</span><meter min="0" max={Math.max(...Object.values(overview.muscle_group_sets), 1)} value={count} aria-label={`${group} sets`}></meter><strong>{count}</strong></div>{/each}</div></section>
      <section class="data-section"><h3>Workouts by split</h3><div class="distribution-list">{#each Object.entries(overview.splits).sort((first, second) => second[1] - first[1]) as [split, count]}<div><span>{formatSplit(split)}</span><meter min="0" max={Math.max(...Object.values(overview.splits), 1)} value={count} aria-label={`${split} workouts`}></meter><strong>{count}</strong></div>{/each}</div></section>
    </div>
    <section class="data-section" aria-label="Progress sessions">
      <div class="section-heading"><h2>{selectedIds.length ? "Selected sessions" : "Exercise sessions"}</h2>{#if selectedIds.length}<button type="button" class="secondary-button" onclick={() => { selectedIds = []; showAll = false; }}><X size={16} /> Clear selection</button>{/if}<span>{displayedSessions.length} of {tableSessions.length}</span></div>
      <div class="table-wrap"><table><thead><tr><th>Date</th><th>Program</th><th class="numeric">Sets</th><th class="numeric">Reps</th><th class="numeric">Known kg-reps</th><th class="numeric">Est. 1RM</th><th></th></tr></thead><tbody>
        {#each displayedSessions as session}<tr><td><time datetime={session.date}>{formatDate(session.date)}</time></td><td class="wrap-cell">{session.program_name || "Unassigned"}{#if session.unusual}<span class="data-flag">Unusual estimate</span>{/if}</td><td class="numeric">{session.sets}</td><td class="numeric">{session.reps}</td><td class="numeric">{number(session.volume_kg_reps, 0)}</td><td class="numeric">{number(session.estimated_one_rm_kg)} kg</td><td><button class="row-action" type="button" aria-label={`Open progress workout from ${formatDate(session.date)}`} title="Open workout" onclick={() => onOpen(session.workout_id)}><CalendarDays size={16} /></button></td></tr>{/each}
      </tbody></table></div>
      {#if !tableSessions.length}<p class="empty-line">No exercise sessions in this period</p>{/if}
      {#if tableSessions.length > 25}<button type="button" class="secondary-button table-toggle" onclick={() => { showAll = !showAll; }}>{showAll ? "Show latest 25" : "Show all sessions"}</button>{/if}
    </section>
  {/if}
</section>