import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, fetchWorkoutPage, fetchYears } from "./api";

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
});