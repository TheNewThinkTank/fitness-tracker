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
  version: z.number().int().positive().default(1),
  gym: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  bodyweight_kg: z.number().positive().nullable().optional(),
  rpe: z.number().nullable().optional(),
  rir: z.number().int().nullable().optional(),
  program_id: z.string().nullable().optional(),
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

const workoutInputSchema = workoutDetailSchema
  .omit({ id: true, year: true, exercise_count: true, set_count: true, version: true })
  .extend({
    date: z.iso.date().refine((value) => value >= "1900-01-01" && value <= "2100-12-31", "Workout date must be between 1900 and 2100"),
    start_time: z.iso.time().nullable(),
    end_time: z.iso.time().nullable(),
    gym: z.string().max(200).nullable().optional(),
    notes: z.string().max(5000).nullable().optional(),
    bodyweight_kg: z.number().positive().max(500).nullable().optional(),
    rpe: z.number().min(1).max(10).nullable().optional(),
    rir: z.number().int().min(0).max(20).nullable().optional(),
    program_id: z.string().max(100).nullable().optional(),
    exercises: z.record(
      z.string().regex(/^[a-zA-Z0-9_()\-]{1,100}$/, "Use a valid exercise name"),
      z.array(exerciseSetSchema.extend({
        set_number: z.number().int().positive(),
        reps: z.number().int().min(0).max(10000),
        weight: z.string().max(200),
        duration: z.string().max(100).nullable().optional(),
        load_multiplier: z.number().int().min(1).max(2).optional(),
      })).min(1).max(100).refine(
        (sets) => new Set(sets.map((entry) => entry.set_number)).size === sets.length,
        "Set numbers must be unique within each exercise",
      ),
    ).refine((exercises) => Object.keys(exercises).length >= 1 && Object.keys(exercises).length <= 100, "Include between 1 and 100 exercises"),
  })
  .strict()
  .superRefine((workout, context) => {
    if (Boolean(workout.start_time) !== Boolean(workout.end_time)) {
      context.addIssue({ code: "custom", path: [workout.start_time ? "end_time" : "start_time"], message: "Provide both start and end times, or leave both empty" });
    } else if (workout.start_time && workout.end_time) {
      const [startHours, startMinutes, startSeconds = 0] = workout.start_time.split(":").map(Number);
      const [endHours, endMinutes, endSeconds = 0] = workout.end_time.split(":").map(Number);
      const seconds = (endHours * 3600 + endMinutes * 60 + endSeconds - startHours * 3600 - startMinutes * 60 - startSeconds + 86400) % 86400;
      if (!(seconds > 0 && seconds <= 43200)) {
        context.addIssue({ code: "custom", path: ["end_time"], message: "Provide a valid workout time window of at most 12 hours" });
      }
    }
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
export type WorkoutInput = z.input<typeof workoutInputSchema>;

const nullableNumber = z.number().nullable();
const sessionSchema = z.object({
  workout_id: z.uuid(),
  date: z.iso.date(),
  split: z.string().nullable(),
  program_id: z.string().nullable(),
  program_name: z.string().nullable(),
  sets: z.number().int().nonnegative(),
  reps: z.number().int().nonnegative(),
  volume_kg_reps: nullableNumber,
  known_load_sets: z.number().int().nonnegative(),
  excluded_load_sets: z.number().int().nonnegative(),
  duration_minutes: nullableNumber,
  sets_per_minute: nullableNumber,
  best_load_kg: nullableNumber,
  best_reps: nullableNumber,
  estimated_one_rm_kg: nullableNumber,
  relative_strength: nullableNumber,
  assistance_kg: nullableNumber,
  hold_seconds: nullableNumber,
  height_cm: nullableNumber,
  unusual: z.boolean(),
  bodyweight_kg: nullableNumber,
});
const bucketSchema = z.object({
  date: z.iso.date(),
  workouts: z.number().int().nonnegative(),
  active_days: z.number().int().nonnegative(),
  sets: z.number().int().nonnegative(),
  reps: z.number().int().nonnegative(),
  volume_kg_reps: nullableNumber,
  duration_minutes: nullableNumber,
  known_load_sets: z.number().int().nonnegative(),
  excluded_load_sets: z.number().int().nonnegative(),
  workout_ids: z.array(z.uuid()),
});
const changeSchema = z.object({
  current: nullableNumber, previous: nullableNumber, delta: nullableNumber, percent: nullableNumber,
});
const overviewSchema = z.object({
  start: z.iso.date(), end: z.iso.date(), bucket: z.enum(["day", "week", "month"]),
  workouts: z.number().int(), active_days: z.number().int(), sets: z.number().int(), reps: z.number().int(),
  volume_kg_reps: nullableNumber, known_load_sets: z.number().int(), excluded_load_sets: z.number().int(),
  duration_minutes: nullableNumber, duration_workouts: z.number().int(), longest_gap_days: nullableNumber,
  buckets: z.array(bucketSchema), activity: z.array(bucketSchema), sessions: z.array(sessionSchema),
  splits: z.record(z.string(), z.number().int()), muscle_group_sets: z.record(z.string(), z.number().int()),
  comparison: z.record(z.string(), changeSchema), volume_unit: z.string(),
});
const exerciseSchema = z.object({
  id: z.string(), label: z.string(), aliases: z.array(z.string()), muscle_groups: z.array(z.string()),
  workouts: z.number().int(), first_date: z.iso.date(), last_date: z.iso.date(), load_convention: z.string(),
});
const historySchema = z.object({
  exercise_id: z.string(), start: z.iso.date(), end: z.iso.date(), formula: z.enum(["epley", "brzycki", "acsm"]),
  max_estimation_reps: z.number().int(), sessions: z.array(sessionSchema), comparison: z.record(z.string(), changeSchema),
  load_kg: nullableNumber.optional(),
});
const recordSchema = z.object({
  exercise_id: z.string(), metric: z.enum(["load", "reps", "estimated_one_rm", "assistance", "hold", "height"]),
  value: z.number(), unit: z.string(), date: z.iso.date(), workout_id: z.uuid(),
});
const targetSchema = z.object({
  exercise_id: z.string(), sets: z.number().int().positive(), reps_min: nullableNumber,
  reps_max: nullableNumber, max_reps: z.boolean(),
});
const programSplitSchema = z.object({ id: z.string(), targets: z.array(targetSchema) });
const programSchema = z.object({
  id: z.string(), name: z.string(), start: z.iso.date(), end: z.iso.date().nullable(), splits: z.array(z.string()),
  planned_workouts: nullableNumber, targets: z.array(programSplitSchema),
});
const programProgressSchema = z.object({
  program: programSchema, workouts: z.number().int(), completion_percent: nullableNumber, sets: z.number().int(),
  volume_kg_reps: nullableNumber, target_sets: z.number().int(), checked_sets: z.number().int(),
  within_rep_range: z.number().int(), rep_adherence_percent: nullableNumber,
});
const measurementSchema = z.object({
  date: z.iso.date(), weight_kg: nullableNumber, waist_cm: nullableNumber, resting_heart_rate: nullableNumber,
});
const authSchema = z.object({
  authenticated: z.boolean(), auth_required: z.boolean(), writes_enabled: z.boolean(), csrf_token: z.string().nullable(),
});
const importSchema = z.object({ imported: z.number().int().nonnegative() });

export type SessionMetrics = z.infer<typeof sessionSchema>;
export type TrainingOverview = z.infer<typeof overviewSchema>;
export type ExerciseInfo = z.infer<typeof exerciseSchema>;
export type ExerciseHistory = z.infer<typeof historySchema>;
export type PersonalRecord = z.infer<typeof recordSchema>;
export type ProgramProgress = z.infer<typeof programProgressSchema>;
export type ProgramSplit = z.infer<typeof programSplitSchema>;
export type BodyMeasurement = z.infer<typeof measurementSchema>;
export type AuthStatus = z.infer<typeof authSchema>;
export type Formula = "epley" | "brzycki" | "acsm";
export interface AnalyticsQuery { from?: string; to?: string; bucket?: "day" | "week" | "month"; formula?: Formula; exercise_id?: string; load_kg?: number }
let csrfToken: string | null = null;

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
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((entry: { msg?: string; loc?: string[] }) => `${entry.loc?.slice(1).join(".") || "Input"}: ${entry.msg || "Invalid value"}`).join("; ");
    }
    return response.statusText;
  } catch {
    return response.statusText;
  }
}

async function requestJson<T>(
  path: string,
  schema: z.ZodType<T>,
  signal?: AbortSignal,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  options: RequestInit = {},
): Promise<T> {
  const controller = new AbortController();
  let timedOut = false;
  const abortFromCaller = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", abortFromCaller, { once: true });
  if (signal?.aborted) controller.abort(signal.reason);
  const timeout = globalThis.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    const response = await fetch(`${API_PREFIX}${path}`, {
      ...options,
      headers: { Accept: "application/json", ...options.headers },
      credentials: "same-origin",
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) {
      if (response.status === 401 && !path.startsWith("/auth/") && typeof window !== "undefined") {
        window.dispatchEvent(new Event("fitness-auth-required"));
      }
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

function queryString(query: AnalyticsQuery): string {
  const parameters = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) if (value !== undefined && value !== "") parameters.set(key, String(value));
  const serialized = parameters.toString();
  return serialized ? `?${serialized}` : "";
}

function writeOptions(method: string, payload?: unknown, contentType = "application/json"): RequestInit {
  return {
    method,
    headers: { "Content-Type": contentType, ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}) },
    body: payload === undefined ? undefined : contentType === "application/json" ? JSON.stringify(payload) : String(payload),
  };
}

export function fetchExercises(signal?: AbortSignal): Promise<ExerciseInfo[]> {
  return requestJson("/exercises", z.array(exerciseSchema), signal);
}
export function fetchOverview(query: AnalyticsQuery, signal?: AbortSignal): Promise<TrainingOverview> {
  return requestJson(`/analytics/overview${queryString(query)}`, overviewSchema, signal);
}
export function fetchExerciseHistory(exercise: string, query: AnalyticsQuery, signal?: AbortSignal): Promise<ExerciseHistory> {
  return requestJson(`/analytics/exercises/${encodeURIComponent(exercise)}${queryString(query)}`, historySchema, signal);
}
export function fetchRecords(query: AnalyticsQuery, signal?: AbortSignal): Promise<PersonalRecord[]> {
  return requestJson(`/analytics/records${queryString(query)}`, z.array(recordSchema), signal);
}
export function fetchPrograms(signal?: AbortSignal): Promise<ProgramProgress[]> {
  return requestJson("/programs", z.array(programProgressSchema), signal);
}
export function fetchMeasurements(query: AnalyticsQuery = {}, signal?: AbortSignal): Promise<BodyMeasurement[]> {
  return requestJson(`/body-metrics${queryString(query)}`, z.array(measurementSchema), signal);
}
export async function fetchAuthStatus(): Promise<AuthStatus> {
  const status = await requestJson("/auth/status", authSchema);
  csrfToken = status.csrf_token;
  return status;
}
export async function signIn(password: string): Promise<AuthStatus> {
  const status = await requestJson("/auth/login", authSchema, undefined, DEFAULT_TIMEOUT_MS, writeOptions("POST", { password }));
  csrfToken = status.csrf_token;
  return status;
}
async function requestVoid(path: string, options: RequestInit): Promise<void> {
  const response = await fetch(`${API_PREFIX}${path}`, { ...options, credentials: "same-origin", cache: "no-store", signal: AbortSignal.timeout(DEFAULT_TIMEOUT_MS) });
  if (!response.ok) throw new ApiError(response.status, await getErrorMessage(response));
}
export async function signOut(): Promise<void> {
  await requestVoid("/auth/logout", writeOptions("POST"));
  csrfToken = null;
}
export function saveWorkout(workout: WorkoutInput, original?: WorkoutDetail): Promise<WorkoutDetail> {
  const parsed = workoutInputSchema.safeParse(workout);
  if (!parsed.success) {
    const message = parsed.error.issues.map((issue) => `${issue.path.join(".") || "Workout"}: ${issue.message}`).join("; ");
    return Promise.reject(new ApiError(422, message));
  }
  const options = writeOptions(original ? "PUT" : "POST", parsed.data);
  if (original) options.headers = { ...options.headers, "If-Match": String(original.version) };
  return requestJson(original ? `/workouts/${encodeURIComponent(original.id)}` : "/workouts", workoutDetailSchema, undefined, DEFAULT_TIMEOUT_MS, options);
}
export function deleteWorkout(workout: WorkoutDetail): Promise<void> {
  const options = writeOptions("DELETE");
  options.headers = { ...options.headers, "If-Match": String(workout.version) };
  return requestVoid(`/workouts/${encodeURIComponent(workout.id)}`, options);
}
export function saveMeasurement(measurement: BodyMeasurement): Promise<BodyMeasurement> {
  return requestJson("/body-metrics", measurementSchema, undefined, DEFAULT_TIMEOUT_MS, writeOptions("POST", measurement));
}
export function deleteMeasurement(date: string): Promise<void> {
  return requestVoid(`/body-metrics/${encodeURIComponent(date)}`, writeOptions("DELETE"));
}
export function saveProgramTargets(programId: string, planned_workouts: number | null, targets: ProgramSplit[]): Promise<ProgramProgress[]> {
  return requestJson(`/programs/${encodeURIComponent(programId)}/targets`, z.array(programProgressSchema), undefined, DEFAULT_TIMEOUT_MS, writeOptions("PUT", { planned_workouts, targets }));
}
export async function importFile(file: File, kind: "workouts" | "body-metrics"): Promise<number> {
  if (file.size > 1024 * 1024) throw new ApiError(413, "Imports must be at most 1 MiB");
  const text = await file.text();
  const response = await requestJson(`/${kind}/import`, importSchema, undefined, DEFAULT_TIMEOUT_MS, {
    method: "POST",
    headers: { "Content-Type": kind === "workouts" ? "application/json" : "text/csv", ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}) },
    body: text,
  });
  return response.imported;
}
export async function downloadProgress(query: AnalyticsQuery): Promise<void> {
  const response = await fetch(`${API_PREFIX}/analytics/export${queryString(query)}`, { headers: { Accept: "text/csv" }, credentials: "same-origin", cache: "no-store", signal: AbortSignal.timeout(DEFAULT_TIMEOUT_MS) });
  if (!response.ok) throw new ApiError(response.status, await getErrorMessage(response));
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = "training_progress.csv";
  link.click();
  URL.revokeObjectURL(url);
}