<script lang="ts">
  import { Dumbbell, X } from "@lucide/svelte";

  import type { WorkoutDetail } from "../api";
  import { formatDate, formatSplit } from "../format";

  interface Props {
    state: "loading" | "ready" | "error";
    workout: WorkoutDetail | null;
    error: string;
    onClose: () => void;
  }

  let { state, workout, error, onClose }: Props = $props();
</script>

<aside class="detail-panel" aria-labelledby="detail-title" aria-busy={state === "loading"}>
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

  {#if state === "loading"}
    <div class="loading-state" aria-live="polite">
      <span class="loading-bar"></span>
      <span>Loading workout detail</span>
    </div>
  {:else if state === "error"}
    <div class="detail-error" role="alert">
      <p>{error}</p>
      <button type="button" class="secondary-button" onclick={onClose}>Close</button>
    </div>
  {:else if workout}
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
        <dt>Volume</dt>
        <dd>{workout.set_count} sets across {workout.exercise_count} exercises</dd>
      </div>
    </dl>

    <div class="exercise-list">
      {#each Object.entries(workout.exercises) as [exercise, sets]}
        <section class="exercise-block">
          <div class="exercise-heading">
            <Dumbbell size={17} />
            <h3>{formatSplit(exercise)}</h3>
            <span>{sets.length} sets</span>
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
                <span role="cell">{exerciseSet.weight ?? "Not logged"}</span>
              </div>
            {/each}
          </div>
        </section>
      {/each}
    </div>
  {/if}
</aside>