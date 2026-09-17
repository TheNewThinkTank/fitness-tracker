<script lang="ts">
  import { ChevronLeft, ChevronRight, Clock3 } from "@lucide/svelte";

  import type { WorkoutPage } from "../api";
  import { formatDate, formatSplit } from "../format";

  interface Props {
    page: WorkoutPage;
    onOpen: (workoutId: string) => void;
    onPrevious: () => void;
    onNext: () => void;
  }

  let { page, onOpen, onPrevious, onNext }: Props = $props();

  function pageStart(): number {
    return page.total > 0 ? page.offset + 1 : 0;
  }

  function pageEnd(): number {
    return Math.min(page.offset + page.items.length, page.total);
  }
</script>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Date</th>
        <th>Split</th>
        <th>Time</th>
        <th class="numeric">Exercises</th>
        <th class="numeric">Sets</th>
        <th aria-label="Actions"></th>
      </tr>
    </thead>
    <tbody>
      {#each page.items as workout (workout.id)}
        <tr>
          <td><time datetime={workout.date}>{formatDate(workout.date)}</time></td>
          <td><span class="split-name">{formatSplit(workout.split)}</span></td>
          <td>
            <span class="time-value">
              <Clock3 size={15} /> {workout.start_time ?? "Not logged"}
            </span>
          </td>
          <td class="numeric">{workout.exercise_count}</td>
          <td class="numeric">{workout.set_count}</td>
          <td class="action-cell">
            <button
              class="row-action"
              type="button"
              aria-label={`Open workout from ${formatDate(workout.date)}`}
              title="Open workout"
              onclick={() => onOpen(workout.id)}
            >
              <ChevronRight size={18} />
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<nav class="pagination" aria-label="Workout pages">
  <span>{pageStart()}-{pageEnd()} of {page.total}</span>
  <div>
    <button
      class="icon-button compact"
      type="button"
      aria-label="Previous page"
      title="Previous page"
      disabled={page.offset === 0}
      onclick={onPrevious}
    >
      <ChevronLeft size={18} />
    </button>
    <button
      class="icon-button compact"
      type="button"
      aria-label="Next page"
      title="Next page"
      disabled={page.offset + page.limit >= page.total}
      onclick={onNext}
    >
      <ChevronRight size={18} />
    </button>
  </div>
</nav>