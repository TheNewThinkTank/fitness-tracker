<script lang="ts">
  import { Download, Pencil, Plus, Save, Trash2, Upload, X } from "@lucide/svelte";
  import { onMount } from "svelte";
  import { deleteMeasurement, fetchMeasurements, importFile, saveMeasurement, type BodyMeasurement } from "../api";
  import { formatDate } from "../format";
  import MetricChart from "./MetricChart.svelte";

  interface Props { canEdit?: boolean; refresh?: number; onChanged?: () => void }
  let { canEdit = false, refresh = 0, onChanged }: Props = $props();
  let rows = $state<BodyMeasurement[]>([]);
  let loading = $state(true);
  let busy = $state(false);
  let error = $state("");
  let notice = $state("");
  let metric = $state<"weight_kg" | "waist_cm" | "resting_heart_rate">("weight_kg");
  let from = $state("");
  let to = $state("");
  let measuredDate = $state(new Date().toISOString().slice(0, 10));
  let weight = $state<number | undefined>(undefined);
  let waist = $state<number | undefined>(undefined);
  let heartRate = $state<number | undefined>(undefined);
  let deleting = $state("");
  let upload = $state<HTMLInputElement>();
  let controller: AbortController | null = null;
  let mounted = false;
  const selected = $derived(metric === "weight_kg" ? { label: "Bodyweight", unit: "kg" } : metric === "waist_cm" ? { label: "Waist", unit: "cm" } : { label: "Resting heart rate", unit: "bpm" });

  onMount(() => { void load().then(() => { mounted = true; }); return () => { mounted = false; controller?.abort(); }; });
  $effect(() => { void refresh; if (mounted) void load(); });
  function message(cause: unknown): string { return cause instanceof Error ? cause.message : "Body measurements are unavailable"; }
  async function load(): Promise<void> {
    controller?.abort();
    const active = new AbortController(); controller = active; loading = true; error = "";
    try {
      const result = await fetchMeasurements({ from: from || undefined, to: to || undefined }, active.signal);
      if (!active.signal.aborted) rows = result;
    } catch (cause) { if (!active.signal.aborted) error = message(cause); }
    finally { if (!active.signal.aborted) loading = false; }
  }
  function clear(): void { weight = undefined; waist = undefined; heartRate = undefined; measuredDate = new Date().toISOString().slice(0, 10); }
  function edit(row: BodyMeasurement): void { measuredDate = row.date; weight = row.weight_kg ?? undefined; waist = row.waist_cm ?? undefined; heartRate = row.resting_heart_rate ?? undefined; }
  async function save(): Promise<void> {
    busy = true; error = ""; notice = "";
    try {
      await saveMeasurement({ date: measuredDate, weight_kg: weight ?? null, waist_cm: waist ?? null, resting_heart_rate: heartRate ?? null });
      notice = "Measurement saved"; clear(); await load(); onChanged?.();
    } catch (cause) { error = message(cause); }
    finally { busy = false; }
  }
  async function remove(date: string): Promise<void> {
    busy = true;
    try { await deleteMeasurement(date); deleting = ""; await load(); onChanged?.(); }
    catch (cause) { error = message(cause); }
    finally { busy = false; }
  }
  async function importCsv(): Promise<void> {
    const file = upload?.files?.[0]; if (!file) return;
    busy = true; error = "";
    try { const count = await importFile(file, "body-metrics"); notice = `${count} measurements imported`; await load(); onChanged?.(); }
    catch (cause) { error = message(cause); }
    finally { busy = false; if (upload) upload.value = ""; }
  }
  function exportCsv(): void {
    const text = ["date,weight_kg,waist_cm,resting_heart_rate", ...rows.map((row) => [row.date, row.weight_kg ?? "", row.waist_cm ?? "", row.resting_heart_rate ?? ""].join(","))].join("\n") + "\n";
    const url = URL.createObjectURL(new Blob([text], { type: "text/csv" }));
    const link = document.createElement("a"); link.href = url; link.download = "body_measurements.csv"; link.click(); URL.revokeObjectURL(url);
  }
</script>

<section class="body-metrics-view" aria-label="Body measurements" aria-busy={loading}>
  <div class="section-heading"><h2>Body measurements</h2><div class="action-group">
    <button class="secondary-button" type="button" disabled={!rows.length} onclick={exportCsv}><Download size={16} /> Export CSV</button>
    {#if canEdit}<input class="visually-hidden" bind:this={upload} type="file" accept=".csv,text/csv" aria-label="Import body measurements CSV" onchange={() => void importCsv()} /><button class="secondary-button" type="button" disabled={busy} onclick={() => upload?.click()}><Upload size={16} /> Import CSV</button>{/if}
  </div></div>
  <form class="analytics-controls" onsubmit={(event) => { event.preventDefault(); void load(); }}>
    <label>From<input type="date" aria-label="Measurements start date" bind:value={from} max={to || undefined} /></label>
    <label>To<input type="date" aria-label="Measurements end date" bind:value={to} min={from || undefined} /></label>
    <label>Metric<select aria-label="Body metric" bind:value={metric}><option value="weight_kg">Bodyweight</option><option value="waist_cm">Waist</option><option value="resting_heart_rate">Resting heart rate</option></select></label>
    <button class="secondary-button" type="submit" disabled={loading}>Apply</button>
  </form>
  {#if error}<p class="inline-error" role="alert">{error}</p>{/if}
  {#if notice}<p class="status-line" role="status">{notice}</p>{/if}
  {#if canEdit}<form class="measurement-form data-section" onsubmit={(event) => { event.preventDefault(); void save(); }}>
    <h3><Plus size={18} /> Measurement</h3><div class="form-grid">
      <label>Date<input type="date" aria-label="Measurement date" bind:value={measuredDate} required /></label>
      <label>Bodyweight (kg)<input type="number" aria-label="Bodyweight in kg" min="1" max="500" step="0.1" bind:value={weight} /></label>
      <label>Waist (cm)<input type="number" aria-label="Waist in cm" min="1" max="400" step="0.1" bind:value={waist} /></label>
      <label>Resting heart rate<input type="number" aria-label="Resting heart rate" min="20" max="250" step="1" bind:value={heartRate} /></label>
    </div><div class="action-group"><button class="primary-button" type="submit" disabled={busy || (weight === undefined && waist === undefined && heartRate === undefined)}><Save size={16} /> Save measurement</button><button class="secondary-button" type="button" onclick={clear}><X size={16} /> Clear</button></div>
  </form>{/if}
  {#if loading && !rows.length}<div class="loading-state"><span class="loading-bar"></span>Loading measurements</div>{/if}
  <MetricChart title={selected.label} unit={selected.unit} series={[{ name: selected.label, points: rows.map((row) => ({ date: row.date, value: row[metric] })) }]} />
  <div class="table-wrap data-section"><table><thead><tr><th>Date</th><th class="numeric">Weight (kg)</th><th class="numeric">Waist (cm)</th><th class="numeric">Resting HR</th>{#if canEdit}<th></th>{/if}</tr></thead><tbody>
    {#each [...rows].reverse() as row}<tr><td>{formatDate(row.date)}</td><td class="numeric">{row.weight_kg ?? "Not measured"}</td><td class="numeric">{row.waist_cm ?? "Not measured"}</td><td class="numeric">{row.resting_heart_rate ?? "Not measured"}</td>{#if canEdit}<td class="measurement-actions"><button class="row-action" type="button" title="Edit measurement" aria-label={`Edit measurement from ${row.date}`} onclick={() => edit(row)}><Pencil size={15} /></button>{#if deleting === row.date}<button class="danger-button" type="button" disabled={busy} onclick={() => void remove(row.date)}>Confirm delete</button><button class="row-action" type="button" title="Cancel deletion" aria-label="Cancel measurement deletion" onclick={() => { deleting = ""; }}><X size={15} /></button>{:else}<button class="row-action" type="button" title="Delete measurement" aria-label={`Delete measurement from ${row.date}`} onclick={() => { deleting = row.date; }}><Trash2 size={15} /></button>{/if}</td>{/if}</tr>{/each}
  </tbody></table></div>
  {#if !rows.length && !loading}<p class="empty-line">No body measurements recorded</p>{/if}
</section>