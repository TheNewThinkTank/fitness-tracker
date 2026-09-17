import { z } from "zod";

const API_PREFIX = "/api";
const DEFAULT_TIMEOUT_MS = 8_000;

const workoutSummarySchema = z.object({
  id: z.uuid(),
  year: z.number().int(),
  date: z.iso.date(),
  split: z.string().nullable(),
  start_time: z.string().nullable(),
  end_time: z.string().nullable(),
  timezone: z.string().nullable(),
  exercise_count: z.number().int().nonnegative(),
  set_count: z.number().int().nonnegative(),
});

const exerciseSetSchema = z
  .object({
    set_number: z.number().int().nullable(),
    reps: z.union([z.number(), z.string()]).nullable(),
    weight: z.union([z.number(), z.string()]).nullable(),
    duration: z.string().nullable().optional(),
  })
  .catchall(z.unknown());

const workoutDetailSchema = workoutSummarySchema.extend({
  exercises: z.record(z.string(), z.array(exerciseSetSchema)),
});

const workoutPageSchema = z.object({
  items: z.array(workoutSummarySchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
  offset: z.number().int().nonnegative(),
  year: z.number().int(),
});

export type WorkoutSummary = z.infer<typeof workoutSummarySchema>;
export type ExerciseSet = z.infer<typeof exerciseSetSchema>;
export type WorkoutDetail = z.infer<typeof workoutDetailSchema>;
export type WorkoutPage = z.infer<typeof workoutPageSchema>;

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    return typeof body.detail === "string" ? body.detail : response.statusText;
  } catch {
    return response.statusText;
  }
}

async function requestJson<T>(
  path: string,
  schema: z.ZodType<T>,
  signal?: AbortSignal,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  let timedOut = false;
  const abortFromCaller = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", abortFromCaller, { once: true });
  const timeout = globalThis.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    const response = await fetch(`${API_PREFIX}${path}`, {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new ApiError(response.status, await getErrorMessage(response));
    }
    const parsed = schema.safeParse(await response.json());
    if (!parsed.success) {
      throw new ApiError(502, "The server returned an unexpected response");
    }
    return parsed.data;
  } catch (error) {
    if (timedOut) {
      throw new ApiError(408, "The server took too long to respond");
    }
    throw error;
  } finally {
    globalThis.clearTimeout(timeout);
    signal?.removeEventListener("abort", abortFromCaller);
  }
}

export function fetchYears(signal?: AbortSignal): Promise<number[]> {
  return requestJson("/years", z.array(z.number().int()), signal);
}

export function fetchWorkoutPage(
  year: number,
  limit: number,
  offset: number,
  order: "asc" | "desc",
  signal?: AbortSignal,
): Promise<WorkoutPage> {
  const query = new URLSearchParams({
    year: String(year),
    limit: String(limit),
    offset: String(offset),
    order,
  });
  return requestJson(`/workouts?${query}`, workoutPageSchema, signal);
}

export function fetchWorkout(
  workoutId: string,
  signal?: AbortSignal,
): Promise<WorkoutDetail> {
  return requestJson(
    `/workouts/${encodeURIComponent(workoutId)}`,
    workoutDetailSchema,
    signal,
  );
}