import { expect, test, type Page } from "@playwright/test";

import type { SessionMetrics, WorkoutDetail } from "../src/api";

function workout(
  sequence: number,
  date: string,
  split = "legs",
  exercise = "squat",
): WorkoutDetail {
  return {
    id: `00000000-0000-4000-8000-${String(sequence).padStart(12, "0")}`,
    year: Number(date.slice(0, 4)),
    date,
    split,
    start_time: "09:00",
    end_time: "10:00",
    timezone: "CET",
    exercise_count: 1,
    set_count: 1,
    version: 1,
    exercises: {
      [exercise]: [{ set_number: 1, reps: 8, weight: "40 kg" }],
    },
  };
}

const records = [
  workout(101, "2022-02-08", "chest", "bench_press"),
  workout(102, "2022-02-08", "back", "row"),
  ...Array.from({ length: 30 }, (_, index) =>
    workout(index + 1, `2024-01-${String(index + 1).padStart(2, "0")}`),
  ),
];

function metrics(record: WorkoutDetail): SessionMetrics {
  const sets = Object.values(record.exercises).flat();
  const loads = sets.map((entry) => Number.parseFloat(String(entry.weight)));
  const estimate = Math.max(...sets.map((entry, index) => loads[index] * (1 + Number(entry.reps) / 30)));
  return {
    workout_id: record.id, date: record.date, split: record.split, program_id: "program_test", program_name: "Foundation",
    sets: sets.length, reps: sets.reduce((total, entry) => total + Number(entry.reps), 0),
    volume_kg_reps: sets.reduce((total, entry, index) => total + Number(entry.reps) * loads[index], 0),
    known_load_sets: sets.length, excluded_load_sets: 0, duration_minutes: 60, sets_per_minute: sets.length / 60,
    best_load_kg: Math.max(...loads), best_reps: Math.max(...sets.map((entry) => Number(entry.reps))),
    estimated_one_rm_kg: estimate, relative_strength: null, assistance_kg: null, hold_seconds: null, height_cm: null,
    unusual: false, bodyweight_kg: null,
  };
}

function bucketDate(value: string, mode: string): string {
  const date = new Date(`${value}T12:00:00Z`);
  if (mode === "week") date.setUTCDate(date.getUTCDate() - (date.getUTCDay() + 6) % 7);
  if (mode === "month") date.setUTCDate(1);
  return date.toISOString().slice(0, 10);
}

function activity(rows: WorkoutDetail[], from: string, to: string, mode: string) {
  const result = [];
  const current = new Date(`${bucketDate(from, mode)}T12:00:00Z`);
  while (current.toISOString().slice(0, 10) <= to) {
    const date = current.toISOString().slice(0, 10);
    const matching = rows.filter((row) => bucketDate(row.date, mode) === date);
    const sessions = matching.map(metrics);
    result.push({ date, workouts: matching.length, active_days: new Set(matching.map((row) => row.date)).size,
      sets: sessions.reduce((total, session) => total + session.sets, 0), reps: sessions.reduce((total, session) => total + session.reps, 0),
      volume_kg_reps: sessions.length ? sessions.reduce((total, session) => total + (session.volume_kg_reps || 0), 0) : null,
      duration_minutes: sessions.length ? sessions.length * 60 : null,
      known_load_sets: sessions.length, excluded_load_sets: 0, workout_ids: matching.map((row) => row.id),
    });
    if (mode === "month") current.setUTCMonth(current.getUTCMonth() + 1);
    else current.setUTCDate(current.getUTCDate() + (mode === "week" ? 7 : 1));
  }
  return result;
}

async function mockWorkouts(page: Page): Promise<void> {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname === "/api/auth/status") {
      await route.fulfill({ json: { authenticated: false, auth_required: false, writes_enabled: false, csrf_token: null } });
      return;
    }
    if (url.pathname === "/api/years") {
      await route.fulfill({ json: [2022, 2024] });
      return;
    }
    if (url.pathname === "/api/workouts") {
      const year = Number(url.searchParams.get("year"));
      const limit = Number(url.searchParams.get("limit"));
      const offset = Number(url.searchParams.get("offset"));
      const filtered = records
        .filter((record) => record.year === year)
        .sort((first, second) => first.date.localeCompare(second.date));
      if (url.searchParams.get("order") === "desc") filtered.reverse();
      await route.fulfill({
        json: { items: filtered.slice(offset, offset + limit), year, total: filtered.length, limit, offset },
      });
      return;
    }
    if (url.pathname === "/api/exercises") {
      const names = [...new Set(records.flatMap((record) => Object.keys(record.exercises)))].sort();
      await route.fulfill({ json: names.map((name) => {
        const matching = records.filter((record) => name in record.exercises);
        return { id: name, label: name.replace(/_/g, " "), aliases: [name], muscle_groups: name === "squat" ? ["legs"] : [], workouts: matching.length, first_date: matching[0].date, last_date: matching[matching.length - 1].date, load_convention: "Recorded external load" };
      }) });
      return;
    }
    const from = url.searchParams.get("from") || "2022-02-08";
    const to = url.searchParams.get("to") || "2024-01-30";
    const filtered = records.filter((record) => from <= record.date && record.date <= to);
    if (url.pathname === "/api/analytics/overview") {
      const sessions = filtered.map(metrics);
      const mode = url.searchParams.get("bucket") || "week";
      const volume = sessions.reduce((total, session) => total + (session.volume_kg_reps || 0), 0);
      const comparison = { current: sessions.length, previous: null, delta: null, percent: null };
      await route.fulfill({ json: {
        start: from, end: to, bucket: mode, workouts: filtered.length, active_days: new Set(filtered.map((row) => row.date)).size,
        sets: sessions.length, reps: sessions.length * 8, volume_kg_reps: sessions.length ? volume : null,
        known_load_sets: sessions.length, excluded_load_sets: 0, duration_minutes: sessions.length ? sessions.length * 60 : null,
        duration_workouts: sessions.length, longest_gap_days: 0, buckets: activity(filtered, from, to, mode), activity: activity(filtered, from, to, "day"),
        splits: { legs: filtered.length }, muscle_group_sets: { legs: filtered.length }, sessions,
        comparison: { workouts: comparison, sets: comparison, volume: comparison }, volume_unit: "kg-reps",
      } });
      return;
    }
    if (url.pathname.startsWith("/api/analytics/exercises/")) {
      const exercise = decodeURIComponent(url.pathname.split("/").pop()!);
      await route.fulfill({ json: { exercise_id: exercise, start: from, end: to, formula: url.searchParams.get("formula") || "epley", max_estimation_reps: 10, sessions: filtered.filter((row) => exercise in row.exercises).map(metrics), comparison: {} } });
      return;
    }
    if (url.pathname === "/api/analytics/records") {
      const exercise = url.searchParams.get("exercise_id") || "squat";
      const record = records.find((row) => exercise in row.exercises)!;
      await route.fulfill({ json: [{ exercise_id: exercise, metric: "load", value: 40, unit: "kg", date: record.date, workout_id: record.id }] });
      return;
    }
    if (url.pathname === "/api/analytics/export") {
      await route.fulfill({ body: "workout_id,date,sets\n" + filtered.map((row) => `${row.id},${row.date},1`).join("\n"), contentType: "text/csv", headers: { "Content-Disposition": 'attachment; filename="training_progress.csv"' } });
      return;
    }
    if (url.pathname === "/api/programs") {
      await route.fulfill({ json: [{ program: { id: "program_test", name: "Foundation", start: "2024-01-01", end: null, splits: ["legs"], planned_workouts: 30, targets: [{ id: "legs", targets: [{ exercise_id: "squat", sets: 1, reps_min: 6, reps_max: 10, max_reps: false }] }] }, workouts: 30, completion_percent: 100, sets: 30, volume_kg_reps: 9600, target_sets: 30, checked_sets: 30, within_rep_range: 30, rep_adherence_percent: 100 }] });
      return;
    }
    if (url.pathname === "/api/body-metrics") {
      await route.fulfill({ json: [{ date: "2024-01-01", weight_kg: 80, waist_cm: null, resting_heart_rate: null }, { date: "2024-01-15", weight_kg: 81, waist_cm: 85, resting_heart_rate: 60 }] });
      return;
    }
    const record = records.find((item) => url.pathname === `/api/workouts/${item.id}`);
    await route.fulfill(
      record ? { json: record } : { status: 404, json: { detail: "Workout not found" } },
    );
  });
}

test("selects years and paginates in global date order", async ({ page }) => {
  await mockWorkouts(page);
  await page.goto("/");

  const year = page.getByLabel("Training year");
  const pagination = page.getByRole("navigation", { name: "Workout pages" });
  const rows = page.locator(".log-panel tbody tr");
  await expect(year).toHaveValue("2024");
  await expect(rows).toHaveCount(25);
  await expect(pagination).toContainText("1-25 of 30");
  await expect(page.getByRole("button", { name: "Previous page" })).toBeDisabled();
  await expect(rows.first().locator("time")).toHaveAttribute("datetime", "2024-01-30");

  await page.getByRole("button", { name: "Next page" }).click();
  await expect(rows).toHaveCount(5);
  await expect(pagination).toContainText("26-30 of 30");
  await expect(page.getByRole("button", { name: "Next page" })).toBeDisabled();
  await page.getByRole("button", { name: "Previous page" }).click();
  await expect(pagination).toContainText("1-25 of 30");

  await page.getByRole("button", { name: "Oldest", exact: true }).click();
  await expect(rows.first().locator("time")).toHaveAttribute("datetime", "2024-01-01");
  await year.selectOption("2022");
  await expect(rows).toHaveCount(2);
  await expect(pagination).toContainText("1-2 of 2");
  await expect(page).toHaveTitle("2022 Training | Fitness Tracker");
});

test("opens distinct details for two workouts on the same day", async ({ page }, testInfo) => {
  await mockWorkouts(page);
  await page.goto("/");
  await page.getByLabel("Training year").selectOption("2022");

  await page.getByRole("row").filter({ hasText: "Chest" }).getByRole("button").click();
  const detail = page.getByRole("complementary");
  await expect(detail.getByRole("heading", { name: "Bench press" })).toBeVisible();
  await expect(detail.getByRole("cell", { name: "40 kg" })).toBeVisible();
  await page.getByRole("button", { name: "Close workout detail" }).click();
  await expect(detail).toHaveCount(0);

  await page.getByRole("row").filter({ hasText: "Back" }).getByRole("button").click();
  await expect(detail.getByRole("heading", { name: "row", exact: true })).toBeVisible();
  await expect(detail.getByRole("heading", { name: "Bench press" })).toHaveCount(0);
  await expect(page.locator(".brand-mark")).toBeVisible();
  expect(await page.locator(".brand-mark").evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await testInfo.attach("workout-detail", {
    body: await page.screenshot({ fullPage: true }),
    contentType: "image/png",
  });
});

test("recovers from an API error when Retry is pressed", async ({ page }) => {
  await mockWorkouts(page);
  let failNextRequest = true;
  await page.route("**/api/years", async (route) => {
    if (failNextRequest) {
      failNextRequest = false;
      await route.fulfill({ status: 503, json: { detail: "Training service unavailable" } });
    } else {
      await route.fallback();
    }
  });
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("Training service unavailable");
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await expect(page.locator(".log-panel tbody tr")).toHaveCount(25);
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("connects the deployed browser to the real workout API", async ({ page, request }) => {
  test.skip(!process.env.E2E_BASE_URL, "Set E2E_BASE_URL to run against the container stack");
  const yearsResponse = await request.get("/api/years");
  expect(yearsResponse.ok()).toBe(true);
  const years = (await yearsResponse.json()) as number[];
  expect(years.length).toBeGreaterThan(0);

  await page.goto("/");
  await expect(page.getByLabel("Training year")).toHaveValue(String(years[years.length - 1]));
  await page.getByLabel("Training year").selectOption(String(years[0]));
  const detailResponse = page.waitForResponse((response) =>
    /\/api\/workouts\/[0-9a-f-]+$/.test(response.url()),
  );
  await page.getByRole("button", { name: /^Open workout from/ }).first().click();
  expect((await detailResponse).ok()).toBe(true);
  await expect(page.getByRole("complementary").getByRole("heading", { level: 3 }).first()).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("progress totals cover the full period and export CSV", async ({ page }, testInfo) => {
  await mockWorkouts(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.locator(".log-panel tbody tr")).toHaveCount(5);
  await page.getByRole("tab", { name: "Progress", exact: true }).click();
  await expect(page.locator(".progress-summary .metric-value").first()).toHaveText("30");
  await expect(page.getByLabel("Calendar year", { exact: true })).toHaveValue("2024");
  await page.getByLabel("Progress exercise").selectOption("squat");
  await expect(page.getByRole("region", { name: "Progress sessions" }).locator("tbody tr")).toHaveCount(25);
  await page.getByRole("button", { name: "Show all sessions" }).click();
  await expect(page.getByRole("region", { name: "Progress sessions" }).locator("tbody tr")).toHaveCount(30);
  const canvas = page.locator(".chart-canvas canvas").first();
  await expect(canvas).toBeVisible();
  await expect.poll(() => canvas.evaluate((element: HTMLCanvasElement) => {
    const pixels = element.getContext("2d")!.getImageData(0, 0, element.width, element.height).data;
    let bandPixels = 0;
    for (let index = 3; index < pixels.length; index += 4) if (pixels[index] >= 10 && pixels[index] <= 25) bandPixels++;
    return bandPixels;
  })).toBeGreaterThan(1000);
  expect(await canvas.evaluate((element: HTMLCanvasElement) => {
    const pixels = element.getContext("2d")!.getImageData(0, 0, element.width, element.height).data;
    let visible = 0;
    for (let index = 3; index < pixels.length; index += 4) if (pixels[index] > 0) visible++;
    return visible > 100;
  })).toBe(true);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export CSV" }).click();
  expect((await download).suggestedFilename()).toBe("training_progress.csv");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await testInfo.attach("training-progress", { body: await page.screenshot({ fullPage: true }), contentType: "image/png" });
});

test("calendar and progress tables drill down into a workout", async ({ page }) => {
  await mockWorkouts(page);
  await page.goto("/?view=progress&exercise=squat&from=2024-01-01&to=2024-01-30");
  await page.getByRole("gridcell", { name: "01 Jan 2024: 1 workouts", exact: true }).click();
  await expect(page.getByRole("complementary").getByRole("heading", { name: "squat", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Close workout detail" }).click();
  await page.getByRole("button", { name: "Open progress workout from 30 Jan 2024", exact: true }).click();
  await expect(page.getByRole("complementary").getByRole("heading", { name: "squat", exact: true })).toBeVisible();
});

test("programs and historical body metrics are navigable", async ({ page }) => {
  await mockWorkouts(page);
  await page.goto("/");
  await page.getByRole("tab", { name: "Programs", exact: true }).click();
  await expect(page.getByLabel("Training program", { exact: true })).toHaveValue("program_test");
  await expect(page.getByRole("heading", { name: "Targets", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "View progress", exact: true }).click();
  await expect(page.getByLabel("Progress start date")).toHaveValue("2024-01-01");
  await expect(page.getByLabel("Progress exercise")).toHaveValue("squat");
  await page.getByRole("tab", { name: "Body metrics", exact: true }).click();
  await expect(page.getByRole("region", { name: "Body measurements" }).locator("tbody tr")).toHaveCount(2);
  await page.getByLabel("Body metric", { exact: true }).selectOption("resting_heart_rate");
  await expect(page.getByRole("img", { name: "Resting heart rate (bpm)", exact: true })).toBeVisible();
});

test("production charts render under the strict proxy CSP", async ({ page }) => {
  test.skip(Boolean(process.env.E2E_BASE_URL), "Use the built production preview for the injected CSP check");
  await mockWorkouts(page);
  const violations: string[] = [];
  page.on("console", (message) => { if (message.type() === "error") violations.push(message.text()); });
  await page.route("**/*", async (route) => {
    if (!route.request().isNavigationRequest()) { await route.fallback(); return; }
    const response = await route.fetch();
    await route.fulfill({ response, headers: { ...response.headers(), "Content-Security-Policy": "default-src 'self'; base-uri 'self'; connect-src 'self'; font-src 'self'; form-action 'self'; frame-ancestors 'none'; img-src 'self' data:; object-src 'none'; script-src 'self'; style-src 'self'" } });
  });
  await page.goto("/?view=progress&exercise=squat&from=2024-01-01&to=2024-01-30");
  await expect(page.locator(".chart-grid > figure:first-child canvas")).toBeVisible();
  await page.getByLabel("Progress metric").selectOption("best_load_kg");
  await expect(page.getByRole("img", { name: "Best recorded load (kg)", exact: true })).toBeVisible();
  expect(violations).toEqual([]);
});

test("workout editor accepts canonical names with valid browser constraints", async ({ page }) => {
  await mockWorkouts(page);
  await page.route("**/api/auth/status", (route) => route.fulfill({ json: { authenticated: true, auth_required: true, writes_enabled: true, csrf_token: "test-csrf" } }));
  const errors: string[] = [];
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto("/");
  await page.getByRole("button", { name: "Log workout", exact: true }).click();
  const editor = page.getByRole("dialog");
  const name = editor.getByLabel("Exercise 1 name", { exact: true });
  await name.fill("romanian_deadlift_(rdl)");
  expect(await name.evaluate((input: HTMLInputElement) => { new RegExp(input.pattern, "v"); return input.checkValidity(); })).toBe(true);
  await editor.getByRole("button", { name: "Add set", exact: true }).click();
  await expect(editor.getByLabel("Exercise 1 set 2 reps", { exact: true })).toBeVisible();
  await editor.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(editor).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("deployed analytics return complete typed progress data", async ({ page, request }) => {
  test.skip(!process.env.E2E_BASE_URL, "Set E2E_BASE_URL for real analytics integration");
  const exercises = await request.get("/api/exercises");
  expect(exercises.ok()).toBe(true);
  const entries = await exercises.json() as { id: string }[];
  expect(entries.length).toBeGreaterThan(0);
  await page.goto(`/?view=progress&exercise=${encodeURIComponent(entries[0].id)}`);
  await expect(page.locator(".progress-summary .metric-value").first()).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.getByRole("tab", { name: "Programs", exact: true }).click();
  await expect(page.getByLabel("Training program", { exact: true })).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("authenticated workout and measurement editing works through the proxy", async ({ page }, testInfo) => {
  test.skip(process.env.E2E_WRITE_TESTS !== "1", "Enable only against disposable, password-protected state");
  const date = testInfo.project.name === "desktop" ? "2030-01-01" : "2030-01-02";
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Athlete sign-in" })).toBeVisible();
  await page.getByLabel("Athlete password").fill(process.env.E2E_PASSWORD || "test-only-browser-password");
  await page.getByRole("region", { name: "Athlete sign-in", exact: true }).getByRole("button", { name: "Sign in", exact: true }).click();
  await page.getByRole("button", { name: "Log workout", exact: true }).click();
  const editor = page.getByRole("dialog");
  await editor.getByLabel("Workout date", { exact: true }).fill(date);
  await editor.getByLabel("Exercise 1 name", { exact: true }).fill("bench_press");
  await editor.getByLabel("Exercise 1 set 1 load", { exact: true }).fill("60 kg");
  await editor.getByLabel("Exercise 1 set 1 reps", { exact: true }).fill("5");
  await editor.getByLabel("Workout bodyweight", { exact: true }).fill("80");
  await editor.getByLabel("Workout notes", { exact: true }).fill(`Browser regression ${testInfo.project.name}`);
  const createdResponse = page.waitForResponse((response) => response.url().endsWith("/api/workouts") && response.request().method() === "POST");
  await editor.getByRole("button", { name: "Save workout", exact: true }).click();
  const created = await (await createdResponse).json() as WorkoutDetail;
  expect(created.version).toBe(1);
  await expect(page.getByRole("complementary")).toContainText(`Browser regression ${testInfo.project.name}`);
  await page.getByRole("button", { name: "Edit workout", exact: true }).click();
  await editor.getByLabel("Exercise 1 set 1 reps", { exact: true }).fill("6");
  const updatedResponse = page.waitForResponse((response) => response.url().endsWith(`/api/workouts/${created.id}`) && response.request().method() === "PUT");
  await editor.getByRole("button", { name: "Save workout", exact: true }).click();
  const updated = await (await updatedResponse).json() as WorkoutDetail;
  expect(updated.version).toBe(2);
  expect(updated.id).toBe(created.id);
  await expect(page.getByRole("complementary").getByRole("cell", { name: "6", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Edit workout", exact: true }).click();
  await editor.getByRole("button", { name: "Delete workout", exact: true }).click();
  await editor.getByRole("button", { name: "Confirm delete", exact: true }).click();
  await expect(editor).toHaveCount(0);
  await expect(page.getByRole("status")).toContainText("Workout deleted");

  const imported = { date, split: "push", exercises: { bench_press: [{ set_number: 1, reps: 5, weight: "60 kg" }] } };
  await page.getByLabel("Import workouts JSON", { exact: true }).setInputFiles({ name: "workouts.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(imported)) });
  await expect(page.getByRole("status")).toContainText("1 workouts imported");

  await page.getByRole("tab", { name: "Body metrics", exact: true }).click();
  await page.getByLabel("Measurement date", { exact: true }).fill(date);
  await page.getByLabel("Bodyweight in kg", { exact: true }).fill("80");
  await page.getByRole("button", { name: "Save measurement", exact: true }).click();
  await expect(page.getByRole("region", { name: "Body measurements" }).locator("tbody")).toContainText("80");
  await page.getByLabel("Import body measurements CSV", { exact: true }).setInputFiles({ name: "measurements.csv", mimeType: "text/csv", buffer: Buffer.from(`date,weight_kg\n${date},81\n`) });
  await expect(page.getByRole("region", { name: "Body measurements", exact: true }).getByRole("status")).toContainText("1 measurements imported");
  await page.getByRole("tab", { name: "Programs", exact: true }).click();
  await page.getByRole("button", { name: "Edit targets", exact: true }).click();
  await page.getByLabel("Planned workouts", { exact: true }).fill("40");
  await page.getByRole("button", { name: "Add target", exact: true }).click();
  await page.getByRole("button", { name: "Save targets", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Targets", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Athlete sign-in", exact: true })).toBeVisible();
});