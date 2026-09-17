<script lang="ts">
  import { ArrowDown, ArrowUp } from "@lucide/svelte";

  interface Props {
    years: number[];
    selectedYear: number;
    sortDirection: "newest" | "oldest";
    onYearChange: (year: number) => void;
    onSortChange: (direction: "newest" | "oldest") => void;
  }

  let {
    years,
    selectedYear,
    sortDirection,
    onYearChange,
    onSortChange,
  }: Props = $props();
</script>

<section class="control-band" aria-label="Workout filters">
  <label class="year-control">
    <span>Training year</span>
    <select
      value={selectedYear}
      disabled={years.length === 0}
      onchange={(event) => onYearChange(Number(event.currentTarget.value))}
    >
      {#each [...years].reverse() as year}
        <option value={year}>{year}</option>
      {/each}
    </select>
  </label>

  <div class="sort-control" aria-label="Workout order">
    <span>Order</span>
    <div class="segmented-control">
      <button
        type="button"
        class:active={sortDirection === "newest"}
        aria-pressed={sortDirection === "newest"}
        onclick={() => onSortChange("newest")}
      >
        <ArrowDown size={16} /> Newest
      </button>
      <button
        type="button"
        class:active={sortDirection === "oldest"}
        aria-pressed={sortDirection === "oldest"}
        onclick={() => onSortChange("oldest")}
      >
        <ArrowUp size={16} /> Oldest
      </button>
    </div>
  </div>
</section>