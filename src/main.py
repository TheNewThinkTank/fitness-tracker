"""FastAPI application for querying weight-training data."""

from __future__ import annotations

import datetime
import csv
from io import StringIO
import json
import secrets
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated, Any, Literal
from uuid import UUID

import yaml  # type: ignore
from fastapi import (  # type: ignore
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    Security,
)
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.security import APIKeyHeader  # type: ignore
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger  # type: ignore
from pydantic import BaseModel  # type: ignore

from src.analytics import (
    Bucket,
    ExerciseHistory,
    ExerciseInfo,
    PersonalRecord,
    ProgramProgress,
    TrainingAnalytics,
    TrainingOverview,
)
from src.common.metrics import Formula
from src.common.measurements import BodyMeasurement
from src.common.workout_types import (
    ExerciseSetResponse,
    WorkoutMetadata,
    WorkoutWrite,
    get_workout_id,
)
from src.utils.config import settings, validate_settings  # type: ignore
from src.utils.access_control import auth_required, auth_router, require_read_access, require_write_access, validate_access_settings
from src.utils.set_db_and_table import (  # type: ignore
    TinyDBSingleton,
)
from src.utils.state_store import VersionConflict, state_store
from src.utils.training_metadata import ProgramSplit, load_programs
from src.utils.workout_repository import WorkoutRepository

YearQuery = Annotated[int | None, Query(ge=1900, le=2100)]
RangeStart = Annotated[datetime.date | None, Query(alias="from")]
RangeEnd = Annotated[datetime.date | None, Query(alias="to")]
workout_repository = WorkoutRepository()


class HealthResponse(BaseModel):
    status: str


class MessageResponse(BaseModel):
    message: str


class WorkoutSummary(WorkoutMetadata):
    id: UUID
    year: int
    exercise_count: int
    set_count: int
    version: int = 1


class WorkoutDetail(WorkoutSummary):
    exercises: dict[str, list[ExerciseSetResponse]]


class WorkoutPage(BaseModel):
    items: list[WorkoutSummary]
    total: int
    limit: int
    offset: int
    year: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_settings()
    validate_access_settings()
    try:
        yield
    finally:
        workout_repository.clear()
        TinyDBSingleton.close_all()


app = FastAPI(
    title="Fitness Tracker API",
    version="0.1.0",
    description="Workout archives, progression analytics, and opt-in session-protected editing.",
    lifespan=lifespan,
)

allowed_origins = [str(origin) for origin in settings.get("ALLOWED_ORIGINS", [])]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type", "X-API-Key"],
    )


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_token(
    api_token: Annotated[str | None, Security(api_key_header)],
) -> None:
    """Require a configured API token while remaining open in local mode."""
    expected_token = str(settings.get("API_TOKEN", ""))
    if expected_token and (
        api_token is None
        or not secrets.compare_digest(
            api_token.encode("utf-8"), expected_token.encode("utf-8")
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "ApiKey"},
        )


api = APIRouter(dependencies=[Depends(require_api_token), Depends(require_read_access)])
legacy_api = APIRouter(dependencies=[Depends(require_api_token), Depends(require_read_access)])


def _resolve_year(year: int | None) -> int:
    available_years = workout_repository.years()
    if year is None:
        if not available_years:
            raise HTTPException(status_code=404, detail="No workout data found")
        return available_years[-1]
    if year not in available_years:
        raise HTTPException(status_code=404, detail=f"No workout data for {year}")
    return year


def _to_summary(document_id: int, item: dict[str, Any], year: int) -> WorkoutSummary:
    exercises = item.get("exercises")
    exercise_map = exercises if isinstance(exercises, dict) else {}
    return WorkoutSummary(
        id=get_workout_id(item, year, document_id),
        year=year,
        date=item["date"],
        split=item.get("split"),
        start_time=item.get("start_time"),
        end_time=item.get("end_time"),
        timezone=item.get("timezone"),
        gym=item.get("gym"),
        notes=item.get("notes"),
        bodyweight_kg=item.get("bodyweight_kg"),
        rpe=item.get("rpe"),
        rir=item.get("rir"),
        program_id=item.get("program_id"),
        version=item.get("_version", 1),
        exercise_count=len(exercise_map),
        set_count=sum(
            len(exercise_sets)
            for exercise_sets in exercise_map.values()
            if isinstance(exercise_sets, list)
        ),
    )


def _to_detail(document_id: int, item: dict[str, Any], year: int) -> WorkoutDetail:
    summary = _to_summary(document_id, item, year)
    exercises = item.get("exercises")
    exercise_map = exercises if isinstance(exercises, dict) else {}
    return WorkoutDetail(
        **summary.model_dump(),
        exercises={
            name: [ExerciseSetResponse.model_validate(exercise_set) for exercise_set in sets]
            for name, sets in exercise_map.items()
            if isinstance(sets, list)
        },
    )


def _summaries_for_year(year: int) -> list[WorkoutSummary]:
    return [
        _to_summary(document_id, item, year)
        for document_id, item in workout_repository.documents(year)
    ]


def _set_read_cache(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store" if auth_required() else "private, max-age=60"


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": [{"loc": item["loc"], "msg": item["msg"], "type": item["type"]} for item in error.errors()]})


@app.get("/healthz", response_model=HealthResponse, include_in_schema=False)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/readyz", response_model=HealthResponse, include_in_schema=False)
def readyz() -> HealthResponse:
    try:
        validate_settings()
        validate_access_settings()
        years = workout_repository.years()
        if years:
            workout_repository.documents(years[-1])
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("Readiness check failed: {}", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Workout storage is unavailable") from exc
    return HealthResponse(status="ok")


@app.get("/", response_model=MessageResponse)
def main_page() -> MessageResponse:
    return MessageResponse(message="Hello, athlete. Welcome to your tracker!")


@api.get("/years", response_model=list[int])
def list_years() -> list[int]:
    return workout_repository.years()


@api.get("/workouts", response_model=WorkoutPage)
def list_workouts(
    response: Response,
    year: YearQuery = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    order: Literal["asc", "desc"] = "desc",
) -> WorkoutPage:
    resolved_year = _resolve_year(year)
    documents = workout_repository.documents(resolved_year, descending=order == "desc")
    _set_read_cache(response)
    return WorkoutPage(
        items=[
            _to_summary(document_id, item, resolved_year)
            for document_id, item in documents[offset:offset + limit]
        ],
        total=len(documents),
        limit=limit,
        offset=offset,
        year=resolved_year,
    )


@api.get("/workouts/{workout_id}", response_model=WorkoutDetail)
def get_workout(workout_id: UUID, response: Response) -> WorkoutDetail:
    result = workout_repository.find(workout_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    year, document_id, item = result
    _set_read_cache(response)
    return _to_detail(document_id, item, year)


@api.get("/data", response_model=list[WorkoutDetail], deprecated=True)
def get_data(
    response: Response,
    year: YearQuery = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    order: Literal["asc", "desc"] = "desc",
) -> list[WorkoutDetail]:
    resolved_year = _resolve_year(year)
    documents = workout_repository.documents(resolved_year, descending=order == "desc")
    _set_read_cache(response)
    return [
        _to_detail(document_id, item, resolved_year)
        for document_id, item in documents[offset:offset + limit]
    ]


@api.get("/dates", response_model=list[datetime.date], deprecated=True)
def get_dates(response: Response, year: YearQuery = None) -> list[datetime.date]:
    resolved_year = _resolve_year(year)
    _set_read_cache(response)
    return sorted({summary.date for summary in _summaries_for_year(resolved_year)})


@api.get("/dates_and_splits", response_model=list[WorkoutSummary], deprecated=True)
def get_dates_and_splits(
    response: Response,
    year: YearQuery = None,
) -> list[WorkoutSummary]:
    resolved_year = _resolve_year(year)
    _set_read_cache(response)
    return _summaries_for_year(resolved_year)


@api.get("/dates/{workout_date}", response_model=list[WorkoutDetail], deprecated=True)
def describe_workout(
    workout_date: datetime.date,
    response: Response,
    year: YearQuery = None,
) -> list[WorkoutDetail]:
    resolved_year = _resolve_year(year)
    matches = [
        _to_detail(document_id, item, resolved_year)
        for document_id, item in workout_repository.documents(resolved_year)
        if item.get("date") == workout_date.isoformat()
    ]
    if not matches:
        raise HTTPException(status_code=404, detail="Workout date not found")
    _set_read_cache(response)
    return matches


@legacy_api.get(
    "/{workout_date}/exercises/{exercise}",
    response_model=list[ExerciseSetResponse],
    deprecated=True,
)
def show_exercise(
    workout_date: datetime.date,
    exercise: str,
    response: Response,
    year: YearQuery = None,
) -> list[ExerciseSetResponse]:
    resolved_year = _resolve_year(year)
    exercise_sets: list[ExerciseSetResponse] = []
    for _, item in workout_repository.documents(resolved_year):
        if item.get("date") != workout_date.isoformat():
            continue
        exercises = item.get("exercises")
        if not isinstance(exercises, dict):
            continue
        exercise_sets.extend(
            ExerciseSetResponse.model_validate(exercise_set)
            for exercise_set in exercises.get(exercise, [])
        )
    if not exercise_sets:
        raise HTTPException(status_code=404, detail="Exercise not found for workout date")
    _set_read_cache(response)
    return exercise_sets


def _analytics() -> TrainingAnalytics:
    documents = [
        (year, document_id, record)
        for year in workout_repository.years()
        for document_id, record in workout_repository.documents(year)
    ]
    return TrainingAnalytics(documents, measurements=state_store.measurements())


def _analytics_range(service: TrainingAnalytics, start: datetime.date | None, end: datetime.date | None) -> tuple[datetime.date, datetime.date]:
    try:
        return service.date_range(start, end)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@api.get("/exercises", response_model=list[ExerciseInfo])
def list_exercises(response: Response) -> list[ExerciseInfo]:
    _set_read_cache(response)
    return _analytics().exercises()


@api.get("/analytics/overview", response_model=TrainingOverview)
def training_overview(response: Response, start: RangeStart = None, end: RangeEnd = None, bucket: Bucket = "week") -> TrainingOverview:
    service = _analytics()
    first, last = _analytics_range(service, start, end)
    _set_read_cache(response)
    return service.overview(first, last, bucket)


@api.get("/analytics/exercises/{exercise_id}", response_model=ExerciseHistory)
def exercise_history(exercise_id: str, response: Response, start: RangeStart = None, end: RangeEnd = None, formula: Formula = "epley", load_kg: Annotated[float | None, Query(ge=0, le=5000)] = None) -> ExerciseHistory:
    service = _analytics()
    first, last = _analytics_range(service, start, end)
    _set_read_cache(response)
    return service.history(exercise_id, first, last, formula, load_kg)


@api.get("/analytics/records", response_model=list[PersonalRecord])
def personal_records(response: Response, exercise_id: str | None = None, start: RangeStart = None, end: RangeEnd = None, formula: Formula = "epley") -> list[PersonalRecord]:
    service = _analytics()
    first, last = _analytics_range(service, start, end)
    _set_read_cache(response)
    return service.records(exercise_id, first, last, formula)


@api.get("/programs", response_model=list[ProgramProgress])
def training_programs(response: Response) -> list[ProgramProgress]:
    _set_read_cache(response)
    return _analytics().program_progress()


@api.get("/analytics/export", response_class=Response)
def export_progress(start: RangeStart = None, end: RangeEnd = None, exercise_id: str | None = None, formula: Formula = "epley", load_kg: Annotated[float | None, Query(ge=0, le=5000)] = None) -> Response:
    service = _analytics()
    first, last = _analytics_range(service, start, end)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["workout_id", "date", "sets", "reps", "known_volume_kg_reps", "excluded_load_sets", "best_load_kg", "estimated_one_rm_kg", "duration_minutes", "assistance_kg", "hold_seconds", "height_cm"])
    for session in service.sessions(first, last, exercise_id, formula, load_kg):
        writer.writerow([session.workout_id, session.date, session.sets, session.reps, session.volume_kg_reps, session.excluded_load_sets, session.best_load_kg, session.estimated_one_rm_kg, session.duration_minutes, session.assistance_kg, session.hold_seconds, session.height_cm])
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="training_progress.csv"', "Cache-Control": "no-store"})


class ImportResult(BaseModel):
    imported: int


class ProgramTargetsUpdate(BaseModel):
    planned_workouts: int | None = None
    targets: list[ProgramSplit]


def _validate_program(identifier: str | None) -> None:
    if identifier and identifier not in {program.id for program in load_programs()}:
        raise HTTPException(status_code=422, detail="Unknown workout program")


def _expected_version(value: str | None) -> int:
    if value is None:
        raise HTTPException(status_code=428, detail="Provide the workout version in If-Match")
    try:
        version = int(value.strip('"'))
        if version < 1:
            raise ValueError
        return version
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid workout version") from exc


@api.post("/workouts", response_model=WorkoutDetail, status_code=201, dependencies=[Depends(require_write_access)])
def create_workout(payload: WorkoutWrite, response: Response) -> WorkoutDetail:
    _validate_program(payload.program_id)
    record = {**payload.model_dump(mode="json", exclude_none=True), "id": state_store.new_id()}
    state_store.save_workout(record)
    response.headers["Cache-Control"] = "no-store"
    return _to_detail(0, record, payload.date.year)


@api.put("/workouts/{workout_id}", response_model=WorkoutDetail, dependencies=[Depends(require_write_access)])
def update_workout(workout_id: UUID, payload: WorkoutWrite, response: Response, if_match: Annotated[str | None, Header()] = None) -> WorkoutDetail:
    existing = workout_repository.find(workout_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    _validate_program(payload.program_id)
    record = {**existing[2], **payload.model_dump(mode="json"), "id": str(workout_id)}
    record.pop("_version", None)
    try:
        version = state_store.save_workout(record, expected_version=_expected_version(if_match))
    except VersionConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    response.headers["Cache-Control"] = "no-store"
    return _to_detail(0, {**record, "_version": version}, payload.date.year)


@api.delete("/workouts/{workout_id}", status_code=204, dependencies=[Depends(require_write_access)])
def delete_workout(workout_id: UUID, if_match: Annotated[str | None, Header()] = None) -> Response:
    result = workout_repository.find(workout_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    record = {**result[2], "id": str(workout_id)}
    record.pop("_version", None)
    try:
        state_store.save_workout(record, expected_version=_expected_version(if_match), deleted=True)
    except VersionConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=204, headers={"Cache-Control": "no-store"})


async def _limited_upload(request: Request) -> bytes:
    chunks = []
    length = 0
    async for chunk in request.stream():
        length += len(chunk)
        if length > 1024 * 1024:
            raise HTTPException(status_code=413, detail="Imports must be at most 1 MiB")
        chunks.append(chunk)
    return b"".join(chunks)


@api.post("/workouts/import", response_model=ImportResult, dependencies=[Depends(require_write_access)])
async def import_workouts(request: Request) -> ImportResult:
    try:
        content = json.loads(await _limited_upload(request))
        records = content if isinstance(content, list) else content.get("workouts", [content])
        if not isinstance(records, list) or not 1 <= len(records) <= 1000:
            raise ValueError
        parsed = []
        identifiers = set()
        for record in records:
            supplied_id = UUID(str(record["id"])) if record.get("id") else UUID(state_store.new_id())
            if supplied_id in identifiers or workout_repository.find(supplied_id) is not None or state_store.workout(str(supplied_id)) is not None:
                raise HTTPException(status_code=409, detail="The import contains an existing or duplicate workout ID")
            identifiers.add(supplied_id)
            fields = {name: value for name, value in record.items() if name in WorkoutWrite.model_fields}
            workout = WorkoutWrite.model_validate(fields)
            _validate_program(workout.program_id)
            extra = {name: value for name, value in record.items() if name not in {"year", "exercise_count", "set_count", "version", "_version"}}
            parsed.append({**extra, **workout.model_dump(mode="json", exclude_none=True), "id": str(supplied_id)})
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail="Provide a valid workout JSON object or a list of at most 1000 workouts") from exc
    try:
        state_store.import_workouts(parsed)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="A workout ID already exists; no records were imported") from exc
    return ImportResult(imported=len(parsed))


@api.get("/body-metrics", response_model=list[BodyMeasurement])
def body_metrics(response: Response, start: RangeStart = None, end: RangeEnd = None) -> list[BodyMeasurement]:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="Start date must not be after end date")
    response.headers["Cache-Control"] = "no-store"
    return [BodyMeasurement.model_validate(measurement) for measurement in state_store.measurements()
            if (start is None or measurement["date"] >= start.isoformat()) and (end is None or measurement["date"] <= end.isoformat())]


@api.post("/body-metrics", response_model=BodyMeasurement, dependencies=[Depends(require_write_access)])
def save_body_metric(payload: BodyMeasurement, response: Response) -> BodyMeasurement:
    state_store.save_measurements([payload.model_dump(mode="json", exclude_unset=True)])
    response.headers["Cache-Control"] = "no-store"
    return BodyMeasurement.model_validate(next(measurement for measurement in state_store.measurements() if measurement["date"] == payload.date.isoformat()))


@api.delete("/body-metrics/{measured_date}", status_code=204, dependencies=[Depends(require_write_access)])
def delete_body_metric(measured_date: datetime.date) -> Response:
    if not state_store.delete_measurement(measured_date.isoformat()):
        raise HTTPException(status_code=404, detail="Measurement not found")
    return Response(status_code=204, headers={"Cache-Control": "no-store"})


@api.post("/body-metrics/import", response_model=ImportResult, dependencies=[Depends(require_write_access)])
async def import_body_metrics(request: Request) -> ImportResult:
    try:
        text = (await _limited_upload(request)).decode("utf-8-sig")
        reader = csv.DictReader(StringIO(text))
        allowed = {"date", "weight_kg", "waist_cm", "resting_heart_rate"}
        if not reader.fieldnames or "date" not in reader.fieldnames or set(reader.fieldnames) - allowed or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError
        measurements: list[dict[str, Any]] = []
        seen = set()
        for row in reader:
            if len(measurements) >= 10000 or row.get("date") in seen or None in row:
                raise ValueError
            values: dict[str, Any] = {"date": row["date"]}
            for field in allowed - {"date"}:
                if row.get(field):
                    values[field] = int(row[field]) if field == "resting_heart_rate" else float(row[field])
            measurement = BodyMeasurement.model_validate(values)
            seen.add(row["date"])
            measurements.append(measurement.model_dump(mode="json", exclude_unset=True))
        if not measurements:
            raise ValueError
    except (ValueError, UnicodeError, csv.Error) as exc:
        raise HTTPException(status_code=422, detail="Provide valid CSV with date and weight_kg, waist_cm, or resting_heart_rate; dates must be unique") from exc
    state_store.save_measurements(measurements)
    return ImportResult(imported=len(measurements))


@api.put("/programs/{program_id}/targets", response_model=list[ProgramProgress], dependencies=[Depends(require_write_access)])
def save_program_targets(program_id: str, payload: ProgramTargetsUpdate) -> list[ProgramProgress]:
    _validate_program(program_id)
    if payload.planned_workouts is not None and not 1 <= payload.planned_workouts <= 10000:
        raise HTTPException(status_code=422, detail="Planned workouts must be between 1 and 10000")
    state_store.configure(f"program:{program_id}", payload.model_dump_json())
    return _analytics().program_progress()


app.include_router(api)
app.include_router(legacy_api)
app.include_router(auth_router, dependencies=[Depends(require_api_token)])


@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml() -> Response:
    yaml_data = yaml.safe_dump(app.openapi(), sort_keys=False)
    return Response(content=yaml_data, media_type="application/yaml")