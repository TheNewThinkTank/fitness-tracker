<script lang="ts">
  import { Activity, CalendarDays, ChartLine, ClipboardList, HeartPulse, List, LogIn, LogOut, Plus, RefreshCw, RotateCcw, Upload } from "@lucide/svelte";
  import { onMount } from "svelte";

  import {
    ApiError,
    fetchAuthStatus,
    fetchWorkout,
    fetchWorkoutPage,
    fetchYears,
    importFile,
    signIn,
    signOut,
    type AuthStatus,
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
  type View = "archive" | "progress" | "programs" | "body";
  const views: View[] = ["archive", "progress", "programs", "body"];
  let view: View = "archive";
  let auth: AuthStatus | null = null;
  let password = "";
  let authError = "";
  let signingIn = false;
  let showSignIn = false;
  let showEditor = false;
  let editingWorkout: WorkoutDetail | null = null;
  let requestedExercise = "";
  let refresh = 0;
  let notice = "";
  let importing = false;
  let workoutUpload: HTMLInputElement | undefined;
  $: locked = Boolean(auth?.auth_required && !auth?.authenticated);
  $: canEdit = Boolean(auth?.authenticated && auth?.writes_enabled);

  onMount(() => {
    const parameters = new URLSearchParams(window.location.search);
    const savedView = parameters.get("view");
    if (views.includes(savedView as View)) view = savedView as View;
    requestedExercise = parameters.get("exercise") || "";
    void initializeSession().then(() => {
      const workout = parameters.get("workout");
      if (workout && !locked) void openWorkout(workout);
    });
    window.addEventListener("fitness-auth-required", expireSession);
    return () => {
      listController?.abort();
      detailController?.abort();
      window.removeEventListener("fitness-auth-required", expireSession);
    };
  });

  function expireSession(): void {
    listController?.abort(); detailController?.abort();
    auth = { authenticated: false, auth_required: true, writes_enabled: auth?.writes_enabled || false, csrf_token: null };
    workoutPage = null; selectedWorkout = null; detailState = "idle"; showEditor = false; showSignIn = true;
  }
  async function initializeSession(): Promise<void> {
    try {
      auth = await fetchAuthStatus();
      if (auth.auth_required && !auth.authenticated) { showSignIn = true; listState = "idle"; return; }
      await loadInitialData();
      refresh += 1;
    } catch (error) { listError = userMessage(error); listState = "error"; }
  }
  async function logIn(): Promise<void> {
    signingIn = true; authError = "";
    try { auth = await signIn(password); showSignIn = false; await loadInitialData(); refresh += 1; }
    catch (error) { authError = userMessage(error); }
    finally { signingIn = false; password = ""; }
  }
  async function logOut(): Promise<void> {
    try { await signOut(); expireSession(); auth = await fetchAuthStatus(); }
    catch (error) { authError = userMessage(error); }
  }
  function changeView(next: View): void {
    view = next; notice = ""; closeWorkout();
    const url = new URL(window.location.href); url.searchParams.set("view", next); window.history.replaceState(null, "", url);
  }
  function navigateTabs(event: KeyboardEvent): void {
    const index = views.indexOf(view);
    let next: View | undefined;
    if (event.key === "ArrowRight") next = views[(index + 1) % views.length];
    if (event.key === "ArrowLeft") next = views[(index + views.length - 1) % views.length];
    if (event.key === "Home") next = views[0];
    if (event.key === "End") next = views[views.length - 1];
    if (next) { event.preventDefault(); changeView(next); document.getElementById(`tab-${next}`)?.focus(); }
  }
  function showProgress(exercise: string, from?: string, to?: string | null): void {
    requestedExercise = exercise;
    const url = new URL(window.location.href); url.searchParams.set("exercise", exercise);
    if (from) url.searchParams.set("from", from);
    if (from) url.searchParams.set("to", to || new Date().toISOString().slice(0, 10));
    window.history.replaceState(null, "", url); changeView("progress");
  }
  function editWorkout(workout: WorkoutDetail | null): void { editingWorkout = workout; showEditor = true; }
  async function savedWorkout(workout?: WorkoutDetail): Promise<void> {
    showEditor = false; notice = workout ? "Workout saved" : "Workout deleted";
    if (workout) selectedYear = workout.year;
    await loadInitialData(); refresh += 1;
    if (workout) void openWorkout(workout.id);
  }
  function dataChanged(): void { refresh += 1; void loadInitialData(); }
  async function uploadWorkouts(): Promise<void> {
    const file = workoutUpload?.files?.[0]; if (!file) return;
    importing = true;
    try { const count = await importFile(file, "workouts"); notice = `${count} workouts imported`; await loadInitialData(); refresh += 1; }
    catch (error) { listError = userMessage(error); listState = "error"; }
    finally { importing = false; if (workoutUpload) workoutUpload.value = ""; }
  }

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
      const requestedYear = Number(new URLSearchParams(window.location.search).get("year"));
      selectedYear = years.includes(selectedYear) ? selectedYear : years.includes(requestedYear) ? requestedYear : years[years.length - 1] ?? 0;
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
      const url = new URL(window.location.href); url.searchParams.set("workout", workoutId); window.history.replaceState(null, "", url);
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
    const url = new URL(window.location.href); url.searchParams.set("year", String(year)); window.history.replaceState(null, "", url);
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
    if (typeof window !== "undefined") { const url = new URL(window.location.href); url.searchParams.delete("workout"); window.history.replaceState(null, "", url); }
  }
</script>

<svelte:head>
  <title>{view === "archive" && selectedYear ? `${selectedYear} Training | Fitness Tracker` : view === "archive" ? "Fitness Tracker" : `${view === "body" ? "Body Metrics" : view === "progress" ? "Progress" : "Programs"} | Fitness Tracker`}</title>
</svelte:head>

<header class="app-header">
  <div class="brand-lockup">
    <img src="/kettlebell.png" alt="" class="brand-mark" />
    <div>
      <p class="eyebrow">Training journal</p>
      <h1>Fitness Tracker</h1>
    </div>
  </div>
  <div class="header-actions">
  {#if auth?.authenticated}<button class="header-command" type="button" onclick={() => void logOut()}><LogOut size={17} /> Sign out</button>{:else if auth?.auth_required}<button class="header-command" type="button" onclick={() => { showSignIn = true; }}><LogIn size={17} /> Sign in</button>{/if}
  <button
    class="icon-button"
    type="button"
    title="Refresh workout data"
    aria-label="Refresh workout data"
    disabled={listState === "loading"}
    onclick={() => void initializeSession()}
  >
    <RefreshCw size={19} class={listState === "loading" ? "spinning" : undefined} />
  </button>
  </div>
</header>

<main>
  <div class="view-tabs" role="tablist" aria-label="Training views" tabindex="-1" onkeydown={navigateTabs}>
    <button type="button" role="tab" id="tab-archive" aria-controls="panel-archive" aria-selected={view === "archive"} tabindex={view === "archive" ? 0 : -1} class:active={view === "archive"} onclick={() => changeView("archive")}><List size={18} /> Archive</button>
    <button type="button" role="tab" id="tab-progress" aria-controls="panel-progress" aria-selected={view === "progress"} tabindex={view === "progress" ? 0 : -1} class:active={view === "progress"} onclick={() => changeView("progress")}><ChartLine size={18} /> Progress</button>
    <button type="button" role="tab" id="tab-programs" aria-controls="panel-programs" aria-selected={view === "programs"} tabindex={view === "programs" ? 0 : -1} class:active={view === "programs"} onclick={() => changeView("programs")}><ClipboardList size={18} /> Programs</button>
    <button type="button" role="tab" id="tab-body" aria-controls="panel-body" aria-selected={view === "body"} tabindex={view === "body" ? 0 : -1} class:active={view === "body"} onclick={() => changeView("body")}><HeartPulse size={18} /> Body metrics</button>
  </div>
  {#if notice}<p class="status-line" role="status">{notice}</p>{/if}
  {#if locked || showSignIn}
    <section class="sign-in-panel" aria-labelledby="sign-in-title"><h2 id="sign-in-title">Athlete sign-in</h2><form onsubmit={(event) => { event.preventDefault(); void logIn(); }}><label>Password<input type="password" aria-label="Athlete password" bind:value={password} required maxlength="1024" autocomplete="current-password" /></label>{#if authError}<p class="inline-error" role="alert">{authError}</p>{/if}<button class="primary-button" type="submit" disabled={signingIn}><LogIn size={17} /> {signingIn ? "Signing in" : "Sign in"}</button></form></section>
  {:else}
  <div class="view-content" role="tabpanel" id={`panel-${view}`} aria-labelledby={`tab-${view}`} tabindex="0">
  {#if view === "archive"}
  {#if canEdit}<div class="archive-actions"><button class="primary-button" type="button" onclick={() => editWorkout(null)}><Plus size={17} /> Log workout</button><input class="visually-hidden" type="file" accept=".json,application/json" bind:this={workoutUpload} aria-label="Import workouts JSON" onchange={() => void uploadWorkouts()} /><button class="secondary-button" type="button" disabled={importing} onclick={() => workoutUpload?.click()}><Upload size={17} /> Import JSON</button></div>{/if}
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
      <button type="button" class="secondary-button" onclick={() => void initializeSession()}>
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
        onProgress={(exercise) => showProgress(exercise)}
        onEdit={canEdit ? editWorkout : undefined}
      />
    {/if}
  </div>
  {:else if view === "progress"}
    {#key requestedExercise}{#await import("./components/ProgressView.svelte")}<div class="loading-state">Loading progress</div>{:then component}<svelte:component this={component.default} onOpen={(id: string) => void openWorkout(id)} initialExercise={requestedExercise} {refresh} />{/await}{/key}
  {:else if view === "programs"}
    {#await import("./components/ProgramsView.svelte")}<div class="loading-state">Loading programs</div>{:then component}<svelte:component this={component.default} {canEdit} {refresh} onChanged={dataChanged} onProgress={(from: string, to: string | null, exercise: string) => showProgress(exercise, from, to)} />{/await}
  {:else}
    {#await import("./components/BodyMetricsView.svelte")}<div class="loading-state">Loading measurements</div>{:then component}<svelte:component this={component.default} {canEdit} {refresh} onChanged={dataChanged} />{/await}
  {/if}
  </div>
  {#if view !== "archive" && detailState !== "idle"}<div class="progress-detail"><WorkoutDetailPanel state={detailState} workout={selectedWorkout} error={detailError} onClose={closeWorkout} onProgress={(exercise) => showProgress(exercise)} onEdit={canEdit ? editWorkout : undefined} /></div>{/if}
  {/if}
</main>
{#if showEditor && canEdit}{#await import("./components/WorkoutEditor.svelte")}{:then component}<svelte:component this={component.default} original={editingWorkout} onClose={() => { showEditor = false; }} onSaved={(workout?: WorkoutDetail) => void savedWorkout(workout)} />{/await}{/if}