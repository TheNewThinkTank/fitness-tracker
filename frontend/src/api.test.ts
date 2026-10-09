import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, fetchAuthStatus, fetchOverview, fetchWorkoutPage, fetchYears, saveMeasurement, saveWorkout, type WorkoutDetail, type WorkoutInput } from "./api";

const newWorkout: WorkoutInput = {
  date: "2030-01-02", split: "push", start_time: "23:30", end_time: "00:30", timezone: null,
  gym: "Test gym", notes: "Evening session", program_id: null, bodyweight_kg: 80, rpe: 8, rir: 2,
  exercises: {
    bench_press: [{ set_number: 1, reps: 5, weight: "60 kg", duration: null, height: null, load_multiplier: 1 }],
    dumbbell_row: [{ set_number: 1, reps: 8, weight: "20 kg", load_multiplier: 2 }],
  },
};
const createdWorkout: WorkoutDetail = {
  ...newWorkout, id: "00000000-0000-4000-8000-000000000001", year: 2030, exercise_count: 2, set_count: 2, version: 1,
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("API client", () => {
  it("loads available years from the same-origin API", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify([2022, 2024]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchYears()).resolves.toEqual([2022, 2024]);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/years",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
  });

  it("encodes pagination and global ordering", async () => {
    const page = { items: [], total: 0, limit: 25, offset: 50, year: 2024 };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(page), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await fetchWorkoutPage(2024, 25, 50, "asc");

    expect(fetchMock.mock.calls[0][0]).toBe(
      "/api/workouts?year=2024&limit=25&offset=50&order=asc",
    );
  });

  it("surfaces API detail messages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "No workout data for 2026" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(fetchYears()).rejects.toEqual(
      new ApiError(404, "No workout data for 2026"),
    );
  });

  it("rejects malformed successful responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(["2024"]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(fetchYears()).rejects.toEqual(
      new ApiError(502, "The server returned an unexpected response"),
    );
  });

  it("validates analytics responses before exposing chart data", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ workouts: 10 }), { status: 200 })));
    await expect(fetchOverview({ from: "2026-01-01", to: "2026-02-01" })).rejects.toEqual(new ApiError(502, "The server returned an unexpected response"));
  });

  it("forwards an already-aborted caller signal without waiting for a timeout", async () => {
    const controller = new AbortController();
    controller.abort();
    vi.stubGlobal("fetch", vi.fn(async (_url: string, options: RequestInit) => {
      options.signal?.throwIfAborted();
      return new Response("[]", { status: 200 });
    }));
    await expect(fetchYears(controller.signal)).rejects.toMatchObject({ name: "AbortError" });
  });

  it("uses in-memory CSRF headers and same-origin cookies for writes", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ authenticated: true, auth_required: true, writes_enabled: true, csrf_token: "test-csrf" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ date: "2026-01-01", weight_kg: 80, waist_cm: null, resting_heart_rate: null }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await fetchAuthStatus();
    await saveMeasurement({ date: "2026-01-01", weight_kg: 80, waist_cm: null, resting_heart_rate: null });
    expect(fetchMock).toHaveBeenLastCalledWith("/api/body-metrics", expect.objectContaining({ method: "POST", credentials: "same-origin", cache: "no-store", headers: expect.objectContaining({ "X-CSRF-Token": "test-csrf" }) }));
  });

  it("inserts a complete workout with CSRF protection and no update-only headers", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ authenticated: true, auth_required: true, writes_enabled: true, csrf_token: "insert-csrf" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(createdWorkout), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    await fetchAuthStatus();

    await expect(saveWorkout(newWorkout)).resolves.toEqual(createdWorkout);
    expect(fetchMock).toHaveBeenLastCalledWith("/api/workouts", expect.objectContaining({
      method: "POST", credentials: "same-origin", cache: "no-store",
      headers: { Accept: "application/json", "Content-Type": "application/json", "X-CSRF-Token": "insert-csrf" },
      body: expect.any(String),
    }));
    const options = fetchMock.mock.calls[1][1] as RequestInit;
    expect(JSON.parse(String(options.body))).toEqual(newWorkout);
  });

  it("keeps existing workout updates version-aware", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...createdWorkout, version: 2 }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(saveWorkout(newWorkout, createdWorkout)).resolves.toMatchObject({ id: createdWorkout.id, version: 2 });
    expect(fetchMock).toHaveBeenCalledWith(`/api/workouts/${createdWorkout.id}`, expect.objectContaining({
      method: "PUT", headers: expect.objectContaining({ "If-Match": "1" }),
    }));
  });

  it.each([
    { name: "invalid calendar date", patch: { date: "2030-02-30" } },
    { name: "date below the supported range", patch: { date: "1899-12-31" } },
    { name: "date above the supported range", patch: { date: "2101-01-01" } },
    { name: "unpaired times", patch: { end_time: null } },
    { name: "invalid clock time", patch: { start_time: "25:00" } },
    { name: "zero-length session", patch: { start_time: "09:00", end_time: "09:00" } },
    { name: "session longer than 12 hours", patch: { start_time: "09:00", end_time: "22:00" } },
    { name: "no exercises", patch: { exercises: {} } },
    { name: "invalid exercise name", patch: { exercises: { "../squat": [{ set_number: 1, reps: 8, weight: "40 kg" }] } } },
    { name: "no sets", patch: { exercises: { squat: [] } } },
    { name: "duplicate set numbers", patch: { exercises: { squat: [{ set_number: 1, reps: 8, weight: "40 kg" }, { set_number: 1, reps: 6, weight: "40 kg" }] } } },
    { name: "fractional reps", patch: { exercises: { squat: [{ set_number: 1, reps: 1.5, weight: "40 kg" }] } } },
    { name: "negative reps", patch: { exercises: { squat: [{ set_number: 1, reps: -1, weight: "40 kg" }] } } },
    { name: "numeric load", patch: { exercises: { squat: [{ set_number: 1, reps: 8, weight: 40 }] } } },
    { name: "invalid load multiplier", patch: { exercises: { squat: [{ set_number: 1, reps: 8, weight: "40 kg", load_multiplier: 3 }] } } },
    { name: "nonpositive bodyweight", patch: { bodyweight_kg: 0 } },
    { name: "out-of-range RPE", patch: { rpe: 11 } },
    { name: "fractional RIR", patch: { rir: 1.5 } },
    { name: "oversized notes", patch: { notes: "x".repeat(5001) } },
    { name: "unexpected top-level fields", patch: { unexpected: true } },
  ])("rejects $name before sending a workout", async ({ patch }) => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(saveWorkout({ ...newWorkout, ...patch } as unknown as WorkoutInput)).rejects.toMatchObject({ status: 422 });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it.each([
    { status: 403, detail: "Editing is disabled" },
    { status: 422, detail: "Unknown workout program" },
    { status: 503, detail: "Workout service unavailable" },
  ])("surfaces an insertion failure with status $status", async ({ status, detail }) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail }), { status })));
    await expect(saveWorkout(newWorkout)).rejects.toEqual(new ApiError(status, detail));
  });

  it("does not accept a malformed insertion response as a saved workout", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ date: newWorkout.date }), { status: 201 })));
    await expect(saveWorkout(newWorkout)).rejects.toEqual(new ApiError(502, "The server returned an unexpected response"));
  });
});