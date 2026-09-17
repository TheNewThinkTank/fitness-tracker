"""FastAPI application for querying weight-training data."""

from __future__ import annotations

import datetime
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, Any, Literal
from uuid import UUID

import yaml  # type: ignore
from fastapi import (  # type: ignore
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Response,
    Security,
)
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.security import APIKeyHeader  # type: ignore
from loguru import logger  # type: ignore
from pydantic import BaseModel  # type: ignore

from src.common.workout_types import (
    ExerciseSetResponse,
    WorkoutMetadata,
    get_workout_id,
)
from src.utils.config import settings, validate_settings  # type: ignore
from src.utils.set_db_and_table import (  # type: ignore
    TinyDBSingleton,
    get_available_years,
)
from src.utils.workout_repository import WorkoutRepository

YearQuery = Annotated[int | None, Query(ge=1900, le=2100)]
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
    try:
        yield
    finally:
        workout_repository.clear()
        TinyDBSingleton.close_all()


app = FastAPI(
    title="Fitness Tracker API",
    version="0.1.0",
    description="Read-only API for weight-training workout records.",
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


api = APIRouter(dependencies=[Depends(require_api_token)])


def _resolve_year(year: int | None) -> int:
    available_years = get_available_years()
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
    response.headers["Cache-Control"] = "private, max-age=60"


@app.get("/healthz", response_model=HealthResponse, include_in_schema=False)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/readyz", response_model=HealthResponse, include_in_schema=False)
def readyz() -> HealthResponse:
    try:
        years = get_available_years()
        if not years:
            raise FileNotFoundError("No workout databases found")
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
    return get_available_years()


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


@api.get(
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


app.include_router(api)


@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml() -> Response:
    yaml_data = yaml.safe_dump(app.openapi(), sort_keys=False)
    return Response(content=yaml_data, media_type="application/yaml")