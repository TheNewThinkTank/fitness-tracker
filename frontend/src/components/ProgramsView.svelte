<script lang="ts">
  import { ChartLine, Pencil, Plus, Save, Trash2, X } from "@lucide/svelte";
  import { onMount } from "svelte";
  import { fetchExercises, fetchPrograms, saveProgramTargets, type ExerciseInfo, type ProgramProgress, type ProgramSplit } from "../api";
  import { formatDate, formatSplit } from "../format";

  interface Props { canEdit?: boolean; refresh?: number; onChanged?: () => void; onProgress: (start: string, end: string | null, exercise: string) => void }
  let { canEdit = false, refresh = 0, onChanged, onProgress }: Props = $props();
  let programs = $state<ProgramProgress[]>([]);
  let exercises = $state<ExerciseInfo[]>([]);
  let selectedId = $state("");
  let loading = $state(true);
  let saving = $state(false);
  let editing = $state(false);
  let error = $state("");
  let targets = $state<ProgramSplit[]>([]);
  let planned = $state<number | undefined>(undefined);
  let newSplit = $state("");
  let controller: AbortController | null = null;
  let mounted = false;
  const selected = $derived(programs.find((entry) => entry.program.id === selectedId));

  onMount(() => { void load().then(() => { mounted = true; }); return () => { mounted = false; controller?.abort(); }; });
  $effect(() => { void refresh; if (mounted && !editing) void load(); });
  async function load(): Promise<void> {
    controller?.abort(); const active = new AbortController(); controller = active; loading = true; error = "";
    try {
      const [results, catalog] = await Promise.all([fetchPrograms(active.signal), fetchExercises(active.signal)]);
      if (active.signal.aborted) return;
      programs = results; exercises = catalog;
      if (!results.some((entry) => entry.program.id === selectedId)) selectedId = results[results.length - 1]?.program.id || "";
    } catch (cause) { if (!active.signal.aborted) error = cause instanceof Error ? cause.message : "Programs are unavailable"; }
    finally { if (!active.signal.aborted) loading = false; }
  }
  function beginEditing(): void {
    if (!selected) return;
    targets = selected.program.targets.map((section) => ({ id: section.id, targets: section.targets.map((target) => ({ ...target })) }));
    planned = selected.program.planned_workouts ?? undefined;
    newSplit = selected.program.splits[0] || "full_body";
    editing = true;
  }
  function addTarget(): void {
    let section = targets.find((entry) => entry.id === newSplit);
    if (!section) { section = { id: newSplit, targets: [] }; targets.push(section); }
    section.targets.push({ exercise_id: exercises.find((exercise) => exercise.id === "bench_press")?.id || exercises[0]?.id || "squat", sets: 3, reps_min: 6, reps_max: 8, max_reps: false });
  }
  async function save(): Promise<void> {
    saving = true; error = "";
    try { programs = await saveProgramTargets(selectedId, planned ?? null, targets.filter((section) => section.targets.length)); editing = false; onChanged?.(); }
    catch (cause) { error = cause instanceof Error ? cause.message : "Targets could not be saved"; }
    finally { saving = false; }
  }
</script>

<section class="programs-view" aria-label="Training programs" aria-busy={loading}>
  <div class="section-heading"><h2>Training programs</h2><label>Program<select aria-label="Training program" bind:value={selectedId} disabled={editing}>{#each programs as entry}<option value={entry.program.id}>{entry.program.name} | {entry.program.start}</option>{/each}</select></label></div>
  {#if error}<p class="inline-error" role="alert">{error}</p>{/if}
  {#if loading && !programs.length}<div class="loading-state"><span class="loading-bar"></span>Loading programs</div>{/if}
  {#if selected}
    <div class="program-period"><span>{formatDate(selected.program.start)} to {selected.program.end ? formatDate(selected.program.end) : "Ongoing"}</span><div class="action-group"><button class="secondary-button" type="button" onclick={() => onProgress(selected!.program.start, selected!.program.end, selected!.program.targets[0]?.targets[0]?.exercise_id || "bench_press")}><ChartLine size={16} /> View progress</button>{#if canEdit && !editing}<button class="secondary-button" type="button" onclick={beginEditing}><Pencil size={16} /> Edit targets</button>{/if}</div></div>
    <div class="metric-strip progress-summary">
      <div><span class="metric-value">{selected.workouts}</span><span class="metric-label">logged workouts<small>{selected.program.planned_workouts ?? "No"} planned</small></span></div>
      <div><span class="metric-value">{selected.sets}</span><span class="metric-label">recorded sets</span></div>
      <div><span class="metric-value">{selected.rep_adherence_percent ?? "Not measured"}{selected.rep_adherence_percent === null ? "" : "%"}</span><span class="metric-label">checked sets in rep range<small>{selected.within_rep_range} of {selected.checked_sets} checked</small></span></div>
    </div>
    {#if editing}<form class="target-editor data-section" onsubmit={(event) => { event.preventDefault(); void save(); }}>
      <div class="form-grid"><label>Planned workouts<input type="number" aria-label="Planned workouts" min="1" max="10000" bind:value={planned} /></label><label>Split<select aria-label="Target split" bind:value={newSplit}>{#each selected.program.splits as split}<option value={split}>{formatSplit(split)}</option>{/each}</select></label><button class="secondary-button" type="button" onclick={addTarget}><Plus size={16} /> Add target</button></div>
      <datalist id="target-exercises">{#each exercises as exercise}<option value={exercise.id}></option>{/each}</datalist>
      {#each targets as section}<fieldset><legend>{formatSplit(section.id)}</legend>{#each section.targets as target, index}<div class="target-row">
        <label>Exercise<input aria-label="Target exercise" list="target-exercises" bind:value={target.exercise_id} required /></label>
        <label>Sets<input aria-label="Target sets" type="number" min="1" max="100" bind:value={target.sets} required /></label>
        <label>Min reps<input aria-label="Minimum target reps" type="number" min="0" max="1000" bind:value={target.reps_min} disabled={target.max_reps} required={!target.max_reps} /></label>
        <label>Max reps<input aria-label="Maximum target reps" type="number" min={target.reps_min ?? 0} max="1000" bind:value={target.reps_max} disabled={target.max_reps} required={!target.max_reps} /></label>
        <label class="checkbox-label"><input type="checkbox" bind:checked={target.max_reps} onchange={() => { target.reps_min = target.max_reps ? null : 6; target.reps_max = target.max_reps ? null : 8; }} /> Max reps</label>
        <button class="row-action" type="button" title="Remove target" aria-label={`Remove ${target.exercise_id} target`} onclick={() => section.targets.splice(index, 1)}><Trash2 size={16} /></button>
      </div>{/each}</fieldset>{/each}
      <div class="action-group"><button class="primary-button" type="submit" disabled={saving}><Save size={16} /> Save targets</button><button class="secondary-button" type="button" disabled={saving} onclick={() => { editing = false; }}><X size={16} /> Cancel</button></div>
    </form>{:else}
      <section class="data-section"><h3>Targets</h3>{#each selected.program.targets as section}<div class="target-section"><h4>{formatSplit(section.id)}</h4><div class="table-wrap"><table><thead><tr><th>Exercise</th><th class="numeric">Sets</th><th class="numeric">Rep range</th></tr></thead><tbody>{#each section.targets as target}<tr><td>{formatSplit(target.exercise_id)}</td><td class="numeric">{target.sets}</td><td class="numeric">{target.max_reps ? "Max reps" : `${target.reps_min}-${target.reps_max}`}</td></tr>{/each}</tbody></table></div></div>{/each}{#if !selected.program.targets.length}<p class="empty-line">No structured targets recorded</p>{/if}</section>
    {/if}
  {/if}
  <section class="data-section"><h2>Program history</h2><div class="table-wrap"><table><thead><tr><th>Program</th><th>Period</th><th class="numeric">Logged / planned</th><th class="numeric">Rep range</th></tr></thead><tbody>{#each [...programs].reverse() as entry}<tr><td><button class="text-button" type="button" onclick={() => { selectedId = entry.program.id; editing = false; }}>{entry.program.name}</button></td><td>{entry.program.start} to {entry.program.end || "Ongoing"}</td><td class="numeric">{entry.workouts} / {entry.program.planned_workouts ?? "Not specified"}</td><td class="numeric">{entry.rep_adherence_percent === null ? "Not measured" : `${entry.rep_adherence_percent}%`}</td></tr>{/each}</tbody></table></div></section>
  {#if !programs.length && !loading}<p class="empty-line">No training programs recorded</p>{/if}
</section>