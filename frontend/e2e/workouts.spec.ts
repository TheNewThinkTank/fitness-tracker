import { expect, test, type Page } from "@playwright/test";

import type { WorkoutDetail } from "../src/api";

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

async function mockWorkouts(page: Page): Promise<void> {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
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