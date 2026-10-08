import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, fetchAuthStatus, fetchOverview, fetchWorkoutPage, fetchYears, saveMeasurement } from "./api";

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
});