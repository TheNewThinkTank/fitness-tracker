import { render } from "svelte/server";
import { describe, expect, it } from "vitest";

import App from "./App.svelte";

describe("App", () => {
  it("renders the workout workspace shell", () => {
    const { body } = render(App);

    expect(body).toContain("Fitness Tracker");
    expect(body).toContain("Training year");
    expect(body).toContain("Workout log");
  });

  it("renders workout entry without granting unauthenticated write access", () => {
    const { body } = render(App);

    expect(body).toContain("Log workout");
    expect(body).toMatch(/aria-label="Log workout"[^>]*disabled/);
  });
});