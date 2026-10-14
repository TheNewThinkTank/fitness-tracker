<script lang="ts">
  import { ChartLine, Dumbbell, Pencil, Trash2, X } from "@lucide/svelte";

  import type { WorkoutDetail } from "../api";
  import { formatDate, formatSplit } from "../format";

  interface Props {
    state: "loading" | "ready" | "error";
    workout: WorkoutDetail | null;
    error: string;
    onClose: () => void;
    onProgress?: (exercise: string) => void;
    onEdit?: (workout: WorkoutDetail) => void;
    onDelete?: (workout: WorkoutDetail) => Promise<void>;
  }

  let { state: detailState, workout, error, onClose, onProgress, onEdit, onDelete }: Props = $props();
  let deleteDialog: HTMLDialogElement;
  let deletionTarget = $state<WorkoutDetail | null>(null);
  let deleting = $state(false);
  let deleteError = $state("");

  function confirmDeletion(): void {
    if (!workout || !onDelete) return;
    deletionTarget = workout;
    deleteError = "";
    deleteDialog.showModal();
  }

  async function removeWorkout(): Promise<void> {
    if (!deletionTarget || !onDelete || deleting) return;
    deleting = true;
    deleteError = "";
    try {
      await onDelete(deletionTarget);
      deleteDialog.close();
    } catch (cause) {
      deleteError = cause instanceof Error ? cause.message : "Workout could not be deleted";
    } finally {
      deleting = false;
    }
  }
</script>

<aside class="detail-panel" aria-labelledby="detail-title" aria-busy={detailState === "loading"}>
  <div class="detail-heading">
    <div>
      <p class="eyebrow">Workout detail</p>
      <h2 id="detail-title">{workout ? formatDate(workout.date) : "Loading"}</h2>
    </div>
    <button
      class="icon-button compact"
      type="button"
      title="Close workout detail"
      aria-label="Close workout detail"
      onclick={onClose}
    >
      <X size={18} />
    </button>
  </div>

  {#if detailState === "loading"}
    <div class="loading-state" aria-live="polite">
      <span class="loading-bar"></span>
      <span>Loading workout detail</span>
    </div>
  {:else if detailState === "error"}
    <div class="detail-error" role="alert">
      <p>{error}</p>
      <button type="button" class="secondary-button" onclick={onClose}>Close</button>
    </div>
  {:else if workout}
    {#if onEdit || onDelete}<div class="detail-actions">
      {#if onEdit}<button class="secondary-button" type="button" onclick={() => onEdit?.(workout!)}><Pencil size={16} /> Edit workout</button>{/if}
      {#if onDelete}<button class="danger-button" type="button" onclick={confirmDeletion}><Trash2 size={16} /> Delete workout</button>{/if}
    </div>{/if}
    <dl class="workout-facts">
      <div>
        <dt>Split</dt>
        <dd>{formatSplit(workout.split)}</dd>
      </div>
      <div>
        <dt>Window</dt>
        <dd>{workout.start_time ?? "Not logged"} to {workout.end_time ?? "Not logged"}</dd>
      </div>
      <div>
        <dt>Workload</dt>
        <dd>{workout.set_count} sets across {workout.exercise_count} exercises</dd>
      </div>
      {#if workout.gym}<div><dt>Gym</dt><dd>{workout.gym}</dd></div>{/if}
      {#if workout.bodyweight_kg != null}<div><dt>Bodyweight</dt><dd>{workout.bodyweight_kg} kg</dd></div>{/if}
      {#if workout.rpe != null}<div><dt>RPE</dt><dd>{workout.rpe}</dd></div>{/if}
      {#if workout.rir != null}<div><dt>RIR</dt><dd>{workout.rir}</dd></div>{/if}
    </dl>
    {#if workout.notes}<p class="workout-notes">{workout.notes}</p>{/if}

    <div class="exercise-list">
      {#each Object.entries(workout.exercises) as [exercise, sets]}
        <section class="exercise-block">
          <div class="exercise-heading">
            <Dumbbell size={17} />
            <h3>{formatSplit(exercise)}</h3>
            <span>{sets.length} sets</span>
            {#if onProgress}<button class="row-action" type="button" title="View exercise progress" aria-label={`View ${formatSplit(exercise)} progress`} onclick={() => onProgress?.(exercise)}><ChartLine size={15} /></button>{/if}
          </div>
          <div class="set-grid" role="table" aria-label={`${formatSplit(exercise)} sets`}>
            <div class="set-row set-header" role="row">
              <span role="columnheader">Set</span>
              <span role="columnheader">Reps</span>
              <span role="columnheader">Load</span>
            </div>
            {#each sets as exerciseSet, setIndex}
              <div class="set-row" role="row">
                <span role="cell">{exerciseSet.set_number ?? setIndex + 1}</span>
                <span role="cell">{exerciseSet.reps ?? exerciseSet.duration ?? "Not logged"}</span>
                <span role="cell">{exerciseSet.weight ?? "Not logged"}{#if exerciseSet.load_multiplier === 2}<small class="set-extra">per hand</small>{/if}{#if exerciseSet.duration}<small class="set-extra">Hold: {exerciseSet.duration}</small>{/if}{#if exerciseSet.height != null}<small class="set-extra">Height: {String(exerciseSet.height)}</small>{/if}</span>
              </div>
            {/each}
          </div>
        </section>
      {/each}
    </div>
  {/if}
</aside>

<dialog class="editor-modal confirmation-modal" bind:this={deleteDialog} aria-labelledby="delete-workout-title" oncancel={(event) => { if (deleting) event.preventDefault(); }}>
  <div class="section-heading modal-heading"><h2 id="delete-workout-title">Delete workout</h2><button class="row-action" type="button" title="Close confirmation" aria-label="Close deletion confirmation" disabled={deleting} onclick={() => deleteDialog.close()}><X size={18} /></button></div>
  {#if deletionTarget}<p>Delete the {formatSplit(deletionTarget.split)} workout from {formatDate(deletionTarget.date)}?</p>{/if}
  {#if deleteError}<p class="inline-error" role="alert">{deleteError}</p>{/if}
  <div class="modal-actions"><button class="danger-button" type="button" disabled={deleting} onclick={() => void removeWorkout()}><Trash2 size={16} /> {deleting ? "Deleting" : "Confirm delete"}</button><button class="secondary-button" type="button" disabled={deleting} onclick={() => deleteDialog.close()}>Keep workout</button></div>
</dialog>