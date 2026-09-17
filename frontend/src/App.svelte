<script lang="ts">
  import { Activity, CalendarDays, RefreshCw, RotateCcw } from "@lucide/svelte";
  import { onMount } from "svelte";

  import {
    ApiError,
    fetchWorkout,
    fetchWorkoutPage,
    fetchYears,
    type WorkoutDetail,
    type WorkoutPage,
  } from "./api";
  import WorkoutControls from "./components/WorkoutControls.svelte";
  import WorkoutDetailPanel from "./components/WorkoutDetailPanel.svelte";
  import WorkoutMetrics from "./components/WorkoutMetrics.svelte";
  import WorkoutTable from "./components/WorkoutTable.svelte";

  type ListState = "idle" | "loading" | "ready" | "empty" | "error";
  type DetailState = "idle" | "loading" | "ready" | "error";
  type SortDirection = "newest" | "oldest";

  const pageSize = 25;
  let years: number[] = [];
  let selectedYear = 0;
  let offset = 0;
  let workoutPage: WorkoutPage | null = null;
  let selectedWorkout: WorkoutDetail | null = null;
  let listState: ListState = "idle";
  let detailState: DetailState = "idle";
  let listError = "";
  let detailError = "";
  let sortDirection: SortDirection = "newest";
  let listController: AbortController | null = null;
  let detailController: AbortController | null = null;

  onMount(() => {
    void loadInitialData();
    return () => {
      listController?.abort();
      detailController?.abort();
    };
  });

  function userMessage(error: unknown): string {
    if (error instanceof ApiError) return error.message;
    if (error instanceof TypeError) return "The workout service could not be reached";
    return "Something went wrong while loading workout data";
  }

  function wasAborted(error: unknown): boolean {
    return error instanceof DOMException && error.name === "AbortError";
  }

  async function loadInitialData(): Promise<void> {
    listController?.abort();
    const controller = new AbortController();
    listController = controller;
    listState = "loading";
    listError = "";

    try {
      years = await fetchYears(controller.signal);
      if (years.length === 0) {
        workoutPage = null;
        listState = "empty";
        return;
      }
      selectedYear = years[years.length - 1] ?? 0;
      offset = 0;
      await loadWorkouts();
    } catch (error) {
      if (!wasAborted(error)) {
        listError = userMessage(error);
        listState = "error";
      }
    }
  }

  async function loadWorkouts(): Promise<void> {
    if (!selectedYear) return;

    listController?.abort();
    detailController?.abort();
    const controller = new AbortController();
    listController = controller;
    workoutPage = null;
    selectedWorkout = null;
    detailState = "idle";
    listState = "loading";
    listError = "";

    try {
      const result = await fetchWorkoutPage(
        selectedYear,
        pageSize,
        offset,
        sortDirection === "newest" ? "desc" : "asc",
        controller.signal,
      );
      if (controller.signal.aborted) return;
      workoutPage = result;
      listState = result.total === 0 ? "empty" : "ready";
    } catch (error) {
      if (!wasAborted(error)) {
        listError = userMessage(error);
        listState = "error";
      }
    }
  }

  async function openWorkout(workoutId: string): Promise<void> {
    detailController?.abort();
    const controller = new AbortController();
    detailController = controller;
    selectedWorkout = null;
    detailError = "";
    detailState = "loading";

    try {
      const result = await fetchWorkout(workoutId, controller.signal);
      if (controller.signal.aborted) return;
      selectedWorkout = result;
      detailState = "ready";
    } catch (error) {
      if (!wasAborted(error)) {
        detailError = userMessage(error);
        detailState = "error";
      }
    }
  }

  function changeYear(year: number): void {
    selectedYear = year;
    offset = 0;
    void loadWorkouts();
  }

  function changeSort(direction: SortDirection): void {
    if (sortDirection === direction) return;
    sortDirection = direction;
    offset = 0;
    void loadWorkouts();
  }

  function previousPage(): void {
    if (!workoutPage) return;
    offset = Math.max(0, workoutPage.offset - workoutPage.limit);
    void loadWorkouts();
  }

  function nextPage(): void {
    if (!workoutPage) return;
    offset = workoutPage.offset + workoutPage.limit;
    void loadWorkouts();
  }

  function closeWorkout(): void {
    detailController?.abort();
    selectedWorkout = null;
    detailState = "idle";
    detailError = "";
  }
</script>

<svelte:head>
  <title>{selectedYear ? `${selectedYear} Training | Fitness Tracker` : "Fitness Tracker"}</title>
</svelte:head>

<header class="app-header">
  <div class="brand-lockup">
    <img src="/kettlebell.png" alt="" class="brand-mark" />
    <div>
      <p class="eyebrow">Training archive</p>
      <h1>Fitness Tracker</h1>
    </div>
  </div>
  <button
    class="icon-button"
    type="button"
    title="Refresh workout data"
    aria-label="Refresh workout data"
    disabled={listState === "loading"}
    onclick={() => void loadInitialData()}
  >
    <RefreshCw size={19} class={listState === "loading" ? "spinning" : undefined} />
  </button>
</header>

<main>
  <WorkoutControls
    {years}
    {selectedYear}
    {sortDirection}
    onYearChange={changeYear}
    onSortChange={changeSort}
  />

  {#if workoutPage && listState !== "error"}
    <WorkoutMetrics page={workoutPage} />
  {/if}

  {#if listState === "error"}
    <section class="message-state error-state" role="alert">
      <Activity size={28} />
      <div>
        <h2>Workout data is unavailable</h2>
        <p>{listError}</p>
      </div>
      <button type="button" class="secondary-button" onclick={() => void loadInitialData()}>
        <RotateCcw size={17} /> Retry
      </button>
    </section>
  {:else if listState === "empty"}
    <section class="message-state" aria-live="polite">
      <CalendarDays size={28} />
      <div>
        <h2>No workouts found</h2>
        <p>No year-based workout files are available in the configured data directory.</p>
      </div>
    </section>
  {/if}

  <div class="workspace" class:with-detail={detailState !== "idle"}>
    <section class="log-panel" aria-labelledby="workout-log-title" aria-busy={listState === "loading"}>
      <div class="panel-heading">
        <div>
          <p class="eyebrow">{selectedYear || "Current"}</p>
          <h2 id="workout-log-title">Workout log</h2>
        </div>
        {#if workoutPage}
          <span class="record-count">{workoutPage.total} records</span>
        {/if}
      </div>

      {#if listState === "loading"}
        <div class="loading-state" aria-live="polite">
          <span class="loading-bar"></span>
          <span>Loading workouts</span>
        </div>
      {:else if listState === "ready" && workoutPage}
        <WorkoutTable
          page={workoutPage}
          onOpen={(workoutId) => void openWorkout(workoutId)}
          onPrevious={previousPage}
          onNext={nextPage}
        />
      {/if}
    </section>

    {#if detailState !== "idle"}
      <WorkoutDetailPanel
        state={detailState}
        workout={selectedWorkout}
        error={detailError}
        onClose={closeWorkout}
      />
    {/if}
  </div>
</main>