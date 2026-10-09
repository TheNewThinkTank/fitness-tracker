<script lang="ts">
  import { Minus, Plus, Save, Trash2, X } from "@lucide/svelte";
  import { onMount } from "svelte";
  import { deleteWorkout, fetchExercises, fetchPrograms, saveWorkout, type ExerciseInfo, type ExerciseSet, type ProgramProgress, type WorkoutDetail, type WorkoutInput } from "../api";
  import { formatSplit } from "../format";

  interface Props { original?: WorkoutDetail | null; onClose: () => void; onSaved: (workout?: WorkoutDetail) => void }
  interface EditableSet { reps: number; weight: string; duration: string; height: string; perHand: boolean; extra: ExerciseSet }
  interface EditableExercise { key: string; name: string; sets: EditableSet[] }
  let { original = null, onClose, onSaved }: Props = $props();
  let modal: HTMLDialogElement;
  const today = new Date();
  let date = $state(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`);
  let split = $state("full_body");
  let start = $state("");
  let end = $state("");
  let gym = $state("");
  let notes = $state("");
  let program = $state("");
  let mass = $state<number | undefined>(undefined);
  let rpe = $state<number | undefined>(undefined);
  let rir = $state<number | undefined>(undefined);
  let rows = $state<EditableExercise[]>([]);
  let catalog = $state<ExerciseInfo[]>([]);
  let programs = $state<ProgramProgress[]>([]);
  let busy = $state(false);
  let confirmDelete = $state(false);
  let error = $state("");

  function blankSet(): EditableSet { return { reps: 8, weight: "0 kg", duration: "", height: "", perHand: false, extra: { set_number: 1, reps: 8, weight: "0 kg" } }; }
  onMount(() => {
    if (original) {
      date = original.date; split = original.split || "full_body"; start = original.start_time || ""; end = original.end_time || "";
      gym = original.gym || ""; notes = original.notes || ""; program = original.program_id || "";
      mass = original.bodyweight_kg ?? undefined; rpe = original.rpe ?? undefined; rir = original.rir ?? undefined;
      rows = Object.entries(original.exercises).map(([name, sets]) => ({ key: crypto.randomUUID(), name, sets: sets.map((exerciseSet) => ({ reps: Number(exerciseSet.reps ?? 0), weight: String(exerciseSet.weight ?? "0 kg"), duration: exerciseSet.duration || "", height: exerciseSet.height == null ? "" : String(exerciseSet.height), perHand: exerciseSet.load_multiplier === 2, extra: { ...exerciseSet } })) }));
    } else rows = [{ key: crypto.randomUUID(), name: "", sets: [blankSet()] }];
    const controller = new AbortController();
    void Promise.all([fetchExercises(controller.signal), fetchPrograms(controller.signal)]).then(([exercises, plans]) => { catalog = exercises; programs = plans; }).catch((cause) => { if (!controller.signal.aborted) error = cause instanceof Error ? cause.message : "Exercise metadata is unavailable"; });
    modal.showModal();
    return () => { controller.abort(); modal.close(); };
  });

  async function save(): Promise<void> {
    if (busy) return;
    error = ""; busy = true;
    try {
      const exercises: WorkoutInput["exercises"] = Object.create(null);
      for (const row of rows) {
        const name = row.name.trim().toLowerCase().replace(/ /g, "_");
        if (!name || exercises[name]) throw new Error("Use a distinct name for each exercise");
        exercises[name] = row.sets.map((exerciseSet, index) => ({ ...exerciseSet.extra, set_number: index + 1, reps: exerciseSet.reps, weight: exerciseSet.weight, duration: exerciseSet.duration || null, height: exerciseSet.height || null, load_multiplier: exerciseSet.perHand ? 2 : 1 }));
      }
      const payload: WorkoutInput = { date, split: split.trim(), start_time: start || null, end_time: end || null, timezone: original ? original.timezone : Intl.DateTimeFormat().resolvedOptions().timeZone, gym: gym.trim() || null, notes: notes || null, program_id: program || null, bodyweight_kg: mass ?? null, rpe: rpe ?? null, rir: rir ?? null, exercises };
      const saved = await saveWorkout(payload, original || undefined);
      onSaved(saved);
    } catch (cause) { error = cause instanceof Error ? cause.message : "Workout could not be saved"; modal.scrollTop = 0; }
    finally { busy = false; }
  }
  async function remove(): Promise<void> {
    if (!original || busy) return;
    busy = true;
    try { await deleteWorkout(original); onSaved(); }
    catch (cause) { error = cause instanceof Error ? cause.message : "Workout could not be deleted"; modal.scrollTop = 0; }
    finally { busy = false; }
  }
</script>

<dialog class="editor-modal" bind:this={modal} aria-labelledby="workout-editor-title" oncancel={(event) => { event.preventDefault(); if (!busy) onClose(); }}>
  <form aria-busy={busy} onsubmit={(event) => { event.preventDefault(); void save(); }}>
    <div class="section-heading modal-heading"><h2 id="workout-editor-title">{original ? "Edit workout" : "Log workout"}</h2><button class="row-action" type="button" title="Close editor" aria-label="Close workout editor" disabled={busy} onclick={onClose}><X size={18} /></button></div>
    {#if error}<p class="inline-error" role="alert">{error}</p>{/if}
    <fieldset class="editor-fields" disabled={busy}>
    <div class="form-grid">
      <label>Date<input aria-label="Workout date" type="date" min="1900-01-01" max="2100-12-31" bind:value={date} required /></label>
      <label>Split<input aria-label="Workout split" bind:value={split} required list="workout-splits" /></label>
      <label>Start<input aria-label="Workout start time" type="time" step="1" bind:value={start} /></label>
      <label>End<input aria-label="Workout end time" type="time" step="1" bind:value={end} /></label>
      <label>Gym<input aria-label="Workout gym" bind:value={gym} maxlength="200" /></label>
      <label>Program<select aria-label="Workout program" bind:value={program}><option value="">Date-based</option>{#each programs as entry}<option value={entry.program.id}>{entry.program.name} ({entry.program.start})</option>{/each}</select></label>
      <label>Bodyweight (kg)<input aria-label="Workout bodyweight" type="number" min="0.1" max="500" step="0.1" bind:value={mass} /></label>
      <label>Session RPE<input aria-label="Session RPE" type="number" min="1" max="10" step="0.5" bind:value={rpe} /></label>
      <label>Reps in reserve<input aria-label="Reps in reserve" type="number" min="0" max="20" step="1" bind:value={rir} /></label>
    </div>
    <datalist id="workout-splits">{#each ["push", "pull", "legs", "full_body", "upper_body_a", "upper_body_b", "lower_body_a", "lower_body_b"] as option}<option value={option}></option>{/each}</datalist>
    <datalist id="workout-exercise-names">{#each catalog as item}<option value={item.id}></option>{/each}</datalist>
    {#each rows as exercise, exerciseIndex (exercise.key)}
      <fieldset class="exercise-editor"><legend>Exercise {exerciseIndex + 1}</legend><div class="exercise-editor-heading"><label>Exercise<input aria-label={`Exercise ${exerciseIndex + 1} name`} list="workout-exercise-names" bind:value={exercise.name} required pattern="[a-zA-Z0-9_\(\)\-]+" maxlength="100" /></label><button class="row-action" type="button" title="Remove exercise" aria-label={`Remove exercise ${exerciseIndex + 1}`} disabled={rows.length === 1 || busy} onclick={() => rows.splice(exerciseIndex, 1)}><Trash2 size={16} /></button></div>
      {#each exercise.sets as exerciseSet, setIndex}<div class="set-editor-row">
        <span class="set-index">{setIndex + 1}</span>
        <label>Reps<input type="number" aria-label={`Exercise ${exerciseIndex + 1} set ${setIndex + 1} reps`} min="0" max="10000" step="1" bind:value={exerciseSet.reps} required /></label>
        <label>Load<input aria-label={`Exercise ${exerciseIndex + 1} set ${setIndex + 1} load`} bind:value={exerciseSet.weight} required maxlength="200" /></label>
        <label>Hold<input aria-label={`Exercise ${exerciseIndex + 1} set ${setIndex + 1} duration`} bind:value={exerciseSet.duration} maxlength="100" /></label>
        <label>Height<input aria-label={`Exercise ${exerciseIndex + 1} set ${setIndex + 1} height`} bind:value={exerciseSet.height} maxlength="100" /></label>
        <label class="checkbox-label"><input type="checkbox" bind:checked={exerciseSet.perHand} /> Per hand</label>
        <button class="row-action" type="button" title="Remove set" aria-label={`Remove exercise ${exerciseIndex + 1} set ${setIndex + 1}`} disabled={exercise.sets.length === 1 || busy} onclick={() => exercise.sets.splice(setIndex, 1)}><Minus size={16} /></button>
      </div>{/each}
      <button class="secondary-button" type="button" disabled={busy || exercise.sets.length >= 100} onclick={() => exercise.sets.push(blankSet())}><Plus size={16} /> Add set</button>
    </fieldset>{/each}
    <button class="secondary-button" type="button" disabled={busy || rows.length >= 100} onclick={() => rows.push({ key: crypto.randomUUID(), name: "", sets: [blankSet()] })}><Plus size={16} /> Add exercise</button>
    <label class="notes-field">Notes<textarea aria-label="Workout notes" bind:value={notes} maxlength="5000" rows="3"></textarea></label>
    </fieldset>
    <div class="modal-actions"><div class="action-group"><button class="primary-button" type="submit" disabled={busy}><Save size={16} /> {busy ? "Saving" : "Save workout"}</button><button class="secondary-button" type="button" disabled={busy} onclick={onClose}>Cancel</button></div>
      {#if original}{#if confirmDelete}<div class="action-group"><button class="danger-button" type="button" disabled={busy} onclick={() => void remove()}>Confirm delete</button><button class="secondary-button" type="button" disabled={busy} onclick={() => { confirmDelete = false; }}>Keep workout</button></div>{:else}<button class="danger-button" type="button" disabled={busy} onclick={() => { confirmDelete = true; }}><Trash2 size={16} /> Delete workout</button>{/if}{/if}
    </div>
  </form>
</dialog>