"""Typed, dependency-light training analytics over validated workout snapshots."""

from collections import Counter, defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.common.metrics import (
    Formula,
    canonical_exercise,
    duration_seconds,
    estimate_one_rm,
    height_cm,
    parse_load,
    positive_number,
    session_duration,
)
from src.common.workout_types import get_workout_id
from src.utils.training_metadata import (
    TrainingProgram,
    exercise_groups,
    load_programs,
    program_for_date,
    split_id,
)

Bucket = Literal["day", "week", "month"]


class ExerciseInfo(BaseModel):
    id: str
    label: str
    aliases: list[str]
    muscle_groups: list[str]
    workouts: int
    first_date: date
    last_date: date
    load_convention: str = "Recorded load; per-hand sets require an explicit multiplier"


class SessionMetrics(BaseModel):
    workout_id: UUID
    date: date
    split: str | None
    program_id: str | None
    program_name: str | None
    sets: int
    reps: int
    volume_kg_reps: float | None
    known_load_sets: int
    excluded_load_sets: int
    duration_minutes: float | None
    sets_per_minute: float | None
    best_load_kg: float | None = None
    best_reps: int | None = None
    estimated_one_rm_kg: float | None = None
    relative_strength: float | None = None
    assistance_kg: float | None = None
    hold_seconds: float | None = None
    height_cm: float | None = None
    unusual: bool = False
    bodyweight_kg: float | None = None


class ActivityBucket(BaseModel):
    date: date
    workouts: int = 0
    active_days: int = 0
    sets: int = 0
    reps: int = 0
    volume_kg_reps: float | None = None
    duration_minutes: float | None = None
    known_load_sets: int = 0
    excluded_load_sets: int = 0
    workout_ids: list[UUID] = Field(default_factory=list)


class MetricChange(BaseModel):
    current: float | None
    previous: float | None
    delta: float | None
    percent: float | None


class TrainingOverview(BaseModel):
    start: date
    end: date
    bucket: Bucket
    workouts: int
    active_days: int
    sets: int
    reps: int
    volume_kg_reps: float | None
    known_load_sets: int
    excluded_load_sets: int
    duration_minutes: float | None
    duration_workouts: int
    longest_gap_days: int | None
    buckets: list[ActivityBucket]
    activity: list[ActivityBucket]
    splits: dict[str, int]
    muscle_group_sets: dict[str, int]
    sessions: list[SessionMetrics]
    comparison: dict[str, MetricChange]
    volume_unit: str = "kg-reps"


class ExerciseHistory(BaseModel):
    exercise_id: str
    start: date
    end: date
    formula: Formula
    max_estimation_reps: int = 10
    load_kg: float | None = None
    sessions: list[SessionMetrics]
    comparison: dict[str, MetricChange]


class PersonalRecord(BaseModel):
    exercise_id: str
    metric: Literal["load", "reps", "estimated_one_rm", "assistance", "hold", "height"]
    value: float
    unit: str
    date: date
    workout_id: UUID


class ProgramProgress(BaseModel):
    program: TrainingProgram
    workouts: int
    completion_percent: float | None
    sets: int
    volume_kg_reps: float | None
    target_sets: int
    checked_sets: int
    within_rep_range: int
    rep_adherence_percent: float | None


def change(current: float | None, previous: float | None) -> MetricChange:
    delta = current - previous if current is not None and previous is not None else None
    return MetricChange(
        current=current,
        previous=previous,
        delta=round(delta, 4) if delta is not None else None,
        percent=round(delta / previous * 100, 2) if delta is not None and previous else None,
    )


def bucket_date(value: date, bucket: Bucket) -> date:
    if bucket == "week":
        return value - timedelta(days=value.weekday())
    if bucket == "month":
        return value.replace(day=1)
    return value


def next_bucket(value: date, bucket: Bucket) -> date:
    if bucket == "month":
        return date(value.year + int(value.month == 12), value.month % 12 + 1, 1)
    return value + timedelta(days=7 if bucket == "week" else 1)


class TrainingAnalytics:
    def __init__(
        self,
        documents: list[tuple[int, int, dict[str, Any]]],
        measurements: list[dict[str, Any]] | None = None,
        programs: list[TrainingProgram] | None = None,
    ) -> None:
        self.documents = sorted(documents, key=lambda row: (row[2]["date"], row[2].get("start_time") or "", str(get_workout_id(row[2], row[0], row[1]))))
        self.measurements = sorted(measurements or [], key=lambda row: row["date"])
        self.programs = load_programs() if programs is None else programs
        self.groups = exercise_groups()

    def date_range(self, start: date | None, end: date | None) -> tuple[date, date]:
        earliest = date.fromisoformat(self.documents[0][2]["date"]) if self.documents else date.today()
        latest = date.fromisoformat(self.documents[-1][2]["date"]) if self.documents else date.today()
        first, last = start or earliest, end or latest
        if first > last:
            raise ValueError("Start date must not be after end date")
        if first.year < 1900 or last.year > 2100 or (last - first).days > 3660:
            raise ValueError("Choose a date range of at most ten years between 1900 and 2100")
        return first, last

    def _mass(self, workout: dict[str, Any]) -> float | None:
        recorded = positive_number(workout.get("bodyweight_kg"))
        if recorded is not None:
            return recorded
        workout_date = date.fromisoformat(workout["date"])
        for measurement in reversed(self.measurements):
            measured_date = date.fromisoformat(str(measurement["date"]))
            if measured_date <= workout_date:
                mass = positive_number(measurement.get("weight_kg"))
                if mass is not None and (workout_date - measured_date).days <= 14:
                    return mass
        return None

    def exercises(self) -> list[ExerciseInfo]:
        entries: dict[str, dict[str, Any]] = {}
        for year, document_id, workout in self.documents:
            for name in (workout.get("exercises") or {}):
                identifier = canonical_exercise(name)
                entry = entries.setdefault(identifier, {"aliases": set(), "dates": [], "workout_ids": set()})
                entry["aliases"].add(name)
                entry["workout_ids"].add(get_workout_id(workout, year, document_id))
                entry["dates"].append(date.fromisoformat(workout["date"]))
        return [ExerciseInfo(
            id=identifier,
            label=identifier.replace("_", " "),
            aliases=sorted(entry["aliases"]),
            muscle_groups=self.groups.get(identifier, []),
            workouts=len(entry["workout_ids"]),
            first_date=min(entry["dates"]),
            last_date=max(entry["dates"]),
        ) for identifier, entry in sorted(entries.items())]

    def _session(
        self, year: int, document_id: int, workout: dict[str, Any],
        exercise_id: str | None = None, formula: Formula = "epley",
        load_kg: float | None = None,
    ) -> SessionMetrics | None:
        exercises = workout.get("exercises") or {}
        selected = [exercise_set for name, sets in exercises.items()
                    if exercise_id is None or canonical_exercise(name) == exercise_id
                    for exercise_set in sets]
        if load_kg is not None:
            selected = [exercise_set for exercise_set in selected
                        if (parsed := parse_load(exercise_set["weight"])).kind == "external"
                        and parsed.total_kg is not None
                        and abs(parsed.total_kg * exercise_set.get("load_multiplier", 1) - load_kg) < 0.001]
        if exercise_id is not None and not selected:
            return None
        mass = self._mass(workout)
        volume = 0.0
        known = 0
        loads, estimates, assistance, holds, heights = [], [], [], [], []
        for exercise_set in selected:
            parsed = parse_load(exercise_set["weight"], mass)
            multiplier = exercise_set.get("load_multiplier", 1)
            multiplier = multiplier if multiplier in (1, 2) else 1
            if parsed.total_kg is not None:
                volume += exercise_set["reps"] * parsed.total_kg * multiplier
                known += 1
            if parsed.kind == "external" and parsed.total_kg is not None:
                loads.append(parsed.total_kg * multiplier)
                estimate = estimate_one_rm(parsed.total_kg * multiplier, exercise_set["reps"], formula)
                if estimate is not None:
                    estimates.append(estimate)
            if parsed.kind in ("bodyweight", "assisted"):
                if parsed.assistance_kg is not None:
                    assistance.append(parsed.assistance_kg)
                elif parsed.reason != "unknown_band_resistance":
                    assistance.append(0.0)
            hold = duration_seconds(exercise_set.get("duration"))
            height = height_cm(exercise_set.get("height"))
            if hold is not None:
                holds.append(hold)
            if height is not None:
                heights.append(height)
        duration = session_duration(workout.get("start_time"), workout.get("end_time"))
        workout_date = date.fromisoformat(workout["date"])
        program = next((program for program in self.programs if program.id == workout.get("program_id")), None)
        program = program or program_for_date(self.programs, workout_date)
        estimated = max(estimates) if estimates else None
        return SessionMetrics(
            workout_id=get_workout_id(workout, year, document_id),
            date=workout_date, split=workout.get("split"),
            program_id=program.id if program else None,
            program_name=program.name if program else None,
            sets=len(selected), reps=sum(exercise_set["reps"] for exercise_set in selected),
            volume_kg_reps=round(volume, 3) if known else None,
            known_load_sets=known, excluded_load_sets=len(selected) - known,
            duration_minutes=duration,
            sets_per_minute=round(len(selected) / duration, 3) if duration is not None else None,
            best_load_kg=max(loads) if loads else None,
            best_reps=max((exercise_set["reps"] for exercise_set in selected), default=None),
            estimated_one_rm_kg=round(estimated, 3) if estimated is not None else None,
            relative_strength=round(estimated / mass, 3) if estimated is not None and mass is not None else None,
            assistance_kg=min(assistance) if assistance else None,
            hold_seconds=max(holds) if holds else None,
            height_cm=max(heights) if heights else None,
            bodyweight_kg=mass,
        )

    def sessions(self, start: date, end: date, exercise_id: str | None = None, formula: Formula = "epley", load_kg: float | None = None) -> list[SessionMetrics]:
        identifier = canonical_exercise(exercise_id) if exercise_id else None
        return [session for year, document_id, workout in self.documents
                if start.isoformat() <= workout["date"] <= end.isoformat()
                if (session := self._session(year, document_id, workout, identifier, formula, load_kg)) is not None]

    @staticmethod
    def _sum(sessions: list[SessionMetrics], field: str) -> float | None:
        values = [getattr(session, field) for session in sessions if getattr(session, field) is not None]
        return round(sum(values), 3) if values else None

    def _buckets(self, sessions: list[SessionMetrics], start: date, end: date, bucket: Bucket) -> list[ActivityBucket]:
        grouped: dict[date, list[SessionMetrics]] = defaultdict(list)
        for session in sessions:
            grouped[bucket_date(session.date, bucket)].append(session)
        result = []
        current = bucket_date(start, bucket)
        while current <= end:
            matching = grouped[current]
            result.append(ActivityBucket(
                date=current, workouts=len(matching), active_days=len({session.date for session in matching}),
                sets=sum(session.sets for session in matching), reps=sum(session.reps for session in matching),
                volume_kg_reps=self._sum(matching, "volume_kg_reps"),
                duration_minutes=self._sum(matching, "duration_minutes"),
                known_load_sets=sum(session.known_load_sets for session in matching),
                excluded_load_sets=sum(session.excluded_load_sets for session in matching),
                workout_ids=[session.workout_id for session in matching],
            ))
            current = next_bucket(current, bucket)
        return result

    def overview(self, start: date | None = None, end: date | None = None, bucket: Bucket = "week") -> TrainingOverview:
        first, last = self.date_range(start, end)
        sessions = self.sessions(first, last)
        previous = self.sessions(first - timedelta(days=(last - first).days + 1), first - timedelta(days=1))
        active_dates = sorted({session.date for session in sessions})
        gaps = [(second - first_date).days - 1 for first_date, second in zip(active_dates, active_dates[1:])]
        group_sets: Counter[str] = Counter()
        for _, _, workout in self.documents:
            if first.isoformat() <= workout["date"] <= last.isoformat():
                for name, sets in (workout.get("exercises") or {}).items():
                    for group in self.groups.get(canonical_exercise(name), ["unmapped"]):
                        group_sets[group] += len(sets)
        volume = self._sum(sessions, "volume_kg_reps")
        return TrainingOverview(
            start=first, end=last, bucket=bucket,
            workouts=len(sessions), active_days=len(active_dates), sets=sum(session.sets for session in sessions),
            reps=sum(session.reps for session in sessions), volume_kg_reps=volume,
            known_load_sets=sum(session.known_load_sets for session in sessions),
            excluded_load_sets=sum(session.excluded_load_sets for session in sessions),
            duration_minutes=self._sum(sessions, "duration_minutes"),
            duration_workouts=sum(session.duration_minutes is not None for session in sessions),
            longest_gap_days=max(gaps) if gaps else None,
            buckets=self._buckets(sessions, first, last, bucket),
            activity=self._buckets(sessions, first, last, "day"),
            splits=dict(Counter(session.split or "unspecified" for session in sessions)),
            muscle_group_sets=dict(group_sets), sessions=sessions,
            comparison={
                "workouts": change(len(sessions), len(previous)),
                "sets": change(sum(session.sets for session in sessions), sum(session.sets for session in previous)),
                "volume": change(volume, self._sum(previous, "volume_kg_reps")),
            },
        )

    def history(self, exercise_id: str, start: date | None = None, end: date | None = None, formula: Formula = "epley", load_kg: float | None = None) -> ExerciseHistory:
        first, last = self.date_range(start, end)
        sessions = self.sessions(first, last, exercise_id, formula, load_kg)
        values = [session.estimated_one_rm_kg for session in sessions if session.estimated_one_rm_kg is not None]
        if len(values) >= 8:
            middle = median(values)
            deviation = median(abs(value - middle) for value in values)
            if deviation > 0:
                for session in sessions:
                    if session.estimated_one_rm_kg is not None:
                        session.unusual = abs(session.estimated_one_rm_kg - middle) > 5.2 * deviation
        current = sessions[-1] if sessions else None
        previous = sessions[-2] if len(sessions) > 1 else None
        comparison = {}
        for label, field in (("load", "best_load_kg"), ("estimated_one_rm", "estimated_one_rm_kg"), ("reps", "best_reps"), ("volume", "volume_kg_reps"), ("assistance", "assistance_kg")):
            comparison[label] = change(getattr(current, field) if current else None, getattr(previous, field) if previous else None)
        return ExerciseHistory(exercise_id=canonical_exercise(exercise_id), start=first, end=last, formula=formula, load_kg=load_kg, sessions=sessions, comparison=comparison)

    def records(self, exercise_id: str | None = None, start: date | None = None, end: date | None = None, formula: Formula = "epley") -> list[PersonalRecord]:
        first, last = self.date_range(start, end)
        identifiers = [canonical_exercise(exercise_id)] if exercise_id else [exercise.id for exercise in self.exercises()]
        result = []
        for identifier in identifiers:
            sessions = self.sessions(first, last, identifier, formula)
            for metric, field, unit in (("load", "best_load_kg", "kg"), ("reps", "best_reps", "reps"), ("estimated_one_rm", "estimated_one_rm_kg", "kg"), ("assistance", "assistance_kg", "kg"), ("hold", "hold_seconds", "seconds"), ("height", "height_cm", "cm")):
                eligible = [session for session in sessions if getattr(session, field) is not None]
                if eligible:
                    best = (min if metric == "assistance" else max)(eligible, key=lambda session: getattr(session, field))
                    result.append(PersonalRecord(exercise_id=identifier, metric=metric, value=getattr(best, field), unit=unit, date=best.date, workout_id=best.workout_id))
        return result

    def program_progress(self) -> list[ProgramProgress]:
        sessions = self.sessions(*self.date_range(None, None))
        result = []
        for program in self.programs:
            matching = [session for session in sessions if session.program_id == program.id]
            targets = {section.id: {target.exercise_id: target for target in section.targets} for section in program.targets}
            target_sets = checked = within = 0
            matching_ids = {session.workout_id for session in matching}
            for year, document_id, workout in self.documents:
                if get_workout_id(workout, year, document_id) not in matching_ids:
                    continue
                prescriptions = targets.get(split_id(workout.get("split") or ""), {})
                target_sets += sum(target.sets for target in prescriptions.values())
                for name, sets in (workout.get("exercises") or {}).items():
                    target = prescriptions.get(canonical_exercise(name))
                    if target and target.reps_min is not None and target.reps_max is not None:
                        checked += len(sets)
                        within += sum(target.reps_min <= exercise_set["reps"] <= target.reps_max for exercise_set in sets)
            result.append(ProgramProgress(
                program=program, workouts=len(matching),
                completion_percent=round(len(matching) / program.planned_workouts * 100, 1) if program.planned_workouts else None,
                sets=sum(session.sets for session in matching), volume_kg_reps=self._sum(matching, "volume_kg_reps"),
                target_sets=target_sets, checked_sets=checked, within_rep_range=within,
                rep_adherence_percent=round(within / checked * 100, 1) if checked else None,
            ))
        return result