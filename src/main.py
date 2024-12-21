"""
Date: 2021-12-11
Purpose: Expose API for training data
Doc: https://fastapi.tiangolo.com/tutorial/first-steps/

To run, execute following command from CLI:
cd src && uvicorn main:app --reload

visit URL: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Response  # type: ignore
# import uvicorn  # type: ignore
from tinydb import TinyDB  # type: ignore
from src.utils.custom_storage import YAMLStorage  # type: ignore
import src.crud.read as read  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from fastapi.openapi.utils import get_openapi  # type: ignore
import yaml  # type: ignore

app = FastAPI()

year = 2024
# TODO: use singleton for db and table
db = TinyDB(f"data/{year}_workouts.yml", storage=YAMLStorage)
table = (db.table("weight_training_log"))
training_catalogue = "src/utils/muscles_and_exercises.yaml"
# db, table, _ = set_db_and_table(datatype="real")


@app.get("/")
async def main_page() -> Response:
    """Returns a greeting message for the application."""
    return Response("Hello, athlete. Welcome to your tracker!")


def greet(name: str) -> None:
    ...


@app.get("/data")
async def get_data():
    """Show data"""
    return [*table]  # Response(f"table data: {table}")


@app.get("/dates")
async def get_dates() -> list[str]:
    """Returns a list of all workout dates."""
    return read.get_dates(table)


@app.get("/dates_and_splits")
async def get_dates_and_splits():  # -> dict[str, list[str]]:
    """Returns a dictionary of workout dates and their corresponding muscle groups."""
    try:
        return read.get_dates_and_muscle_groups(table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/dates/{date}")
async def describe_workout(date: str):  # -> dict[str, str]:
    """Returns a dictionary describing the workout for the given date."""
    if date not in read.get_dates(table):
        raise HTTPException(status_code=404, detail="Workout date not found")
    return read.describe_workout(table, date)


@app.get("/{date}/exercises/{exercise}")
async def show_exercise(exercise: str, date: str) -> list[dict]:
    """Returns a list of sets and reps for the given exercise and date."""
    return read.show_exercise(table, exercise, date)


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
