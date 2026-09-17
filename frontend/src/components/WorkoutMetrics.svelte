<script lang="ts">
  import type { WorkoutPage } from "../api";

  interface Props {
    page: WorkoutPage;
  }

  let { page }: Props = $props();

  function pageStart(): number {
    return page.total > 0 ? page.offset + 1 : 0;
  }

  function pageEnd(): number {
    return Math.min(page.offset + page.items.length, page.total);
  }

  function visibleSetCount(): number {
    return page.items.reduce((total, workout) => total + workout.set_count, 0);
  }
</script>

<section class="metric-strip" aria-label="Year summary">
  <div>
    <span class="metric-value">{page.total}</span>
    <span class="metric-label">workouts logged</span>
  </div>
  <div>
    <span class="metric-value">{visibleSetCount()}</span>
    <span class="metric-label">sets on this page</span>
  </div>
  <div>
    <span class="metric-value">{pageStart()}-{pageEnd()}</span>
    <span class="metric-label">visible records</span>
  </div>
</section>