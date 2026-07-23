"""
Expose API for training data.

Docs: https://fastapi.tiangolo.com/tutorial/first-steps/

To run, execute following command from CLI:
cd src && uvicorn main:app --reload

visit URL: http://127.0.0.1:8000/docs
"""

import datetime
from contextlib import asynccontextmanager
import yaml  # type: ignore
from fastapi import FastAPI, HTTPException, Query, Response  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.openapi.utils import get_openapi  # type: ignore
import src.crud.read as read  # type: ignore
from src.utils.config import validate_settings  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_settings()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_current_year = datetime.date.today().year
db, table, training_catalogue = set_db_and_table(datatype="real", year=_current_year)


def _get_table(year: int):
    if year == _current_year:
        return table
    _, t, _ = set_db_and_table(datatype="real", year=year)
    return t


class HealthResponse(BaseModel):
    status: str


@app.get("/healthz", response_model=HealthResponse, include_in_schema=False)
async def healthz() -> HealthResponse:
    """Liveness probe — confirms the process is running."""
    return HealthResponse(status="ok")


@app.get("/readyz", response_model=HealthResponse, include_in_schema=False)
async def readyz() -> HealthResponse:
    """Readiness probe — confirms the app can serve traffic (DB reachable)."""
    try:
        _ = read.get_dates(table)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {e}")
    return HealthResponse(status="ok")


@app.get("/")
async def main_page() -> Response:
    """Returns a greeting message for the application."""
    return Response("Hello, athlete. Welcome to your tracker!")


@app.get("/data")
async def get_data(year: int = Query(default=None)):
    """Show data"""
    t = _get_table(year or _current_year)
    return [*t]


@app.get("/dates")
async def get_dates(year: int = Query(default=None)) -> list[str]:
    """Returns a list of all workout dates."""
    t = _get_table(year or _current_year)
    return read.get_dates(t)


@app.get("/dates_and_splits")
async def get_dates_and_splits(year: int = Query(default=None)):
    """Returns a dictionary of workout dates and their corresponding muscle groups."""
    try:
        t = _get_table(year or _current_year)
        return read.get_dates_and_muscle_groups(t)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dates/{date}")
async def describe_workout(date: str, year: int = Query(default=None)) -> list[dict] | None:
    """Returns workout summaries for the given date (list because multiple workouts can share a date)."""
    t = _get_table(year or _current_year)
    if date not in read.get_dates(t):
        raise HTTPException(status_code=404, detail="Workout date not found")
    return read.describe_workout(t, date)


@app.get("/{date}/exercises/{exercise}")
async def show_exercise(exercise: str, date: str, year: int = Query(default=None)) -> list[dict]:
    """Returns a list of sets and reps for the given exercise and date."""
    t = _get_table(year or _current_year)
    return read.show_exercise(t, exercise, date)


@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    openapi_schema = get_openapi(
        title="Your API Title",
        version="0.1.0",
        description="Your API Description",
        routes=app.routes,
    )
    yaml_data = yaml.safe_dump(openapi_schema, sort_keys=False)
    return Response(content=yaml_data, media_type="application/x-yaml")


# if __name__ == "__main__":
#     uvicorn.run(app, port=8000, host="0.0.0.0")
