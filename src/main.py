"""
Date: 2021-12-11
Purpose: Expose API for training data
Doc: https://fastapi.tiangolo.com/tutorial/first-steps/

To run, execute following command from CLI:
cd src && uvicorn main:app --reload

visit URL: http://127.0.0.1:8000/docs
"""

__author__ = "Gustav Collin Rasmussen"
__version__ = "0.1.0"

from typing import Dict, List

from fastapi import FastAPI, HTTPException, Response  # type: ignore

# import uvicorn  # type: ignore

import CRUD.read  # type: ignore
from helpers.set_db_and_table import set_db_and_table  # type: ignore

app = FastAPI()
db, table, _ = set_db_and_table(datatype="real")

app = FastAPI()
db, table, _ = set_db_and_table(datatype="real")

def get_dates(table: str) -> List[str]:
    """Returns a list of all workout dates in the table."""
    return CRUD.read.get_dates(table)

def get_dates_and_muscle_groups(table: str) -> Dict[str, List[str]]:
    """Returns a dictionary of workout dates and their corresponding muscle groups."""
    return CRUD.read.get_dates_and_muscle_groups(table)

def describe_workout(table: str, date: str) -> Dict[str, str]:
    """Returns a dictionary describing the workout for the given date."""
    return CRUD.read.describe_workout(table, date)

def show_exercise(table: str, exercise: str, date: str) -> List[str]:
    """Returns a list of sets and reps for the given exercise and date."""
    return CRUD.read.show_exercise(table, exercise, date)

@app.get("/")
async def main_page() -> Response:
    """Returns a greeting message for the application."""
    return Response("Hello, athlete. Welcome to your tracker!")

@app.get("/dates")
async def get_all_dates() -> List[str]:
    """Returns a list of all workout dates."""
    return get_dates(table)

@app.get("/dates_and_splits")
async def get_dates_and_splits() -> Dict[str, List[str]]:
    """Returns a dictionary of workout dates and their corresponding muscle groups."""
    return get_dates_and_muscle_groups(table)

@app.get("/dates/{date}")
async def get_workout_description(date: str) -> Dict[str, str]:
    """Returns a dictionary describing the workout for the given date."""
    if date not in get_dates(table):
        raise HTTPException(status_code=404, detail="Workout date not found")
    return describe_workout(table, date)

@app.get("/{date}/exercises/{exercise}")
async def get_exercise_info(exercise: str, date: str) -> List[str]:
    """Returns a list of sets and reps for the given exercise and date."""
    return show_exercise(table, exercise, date)

# @app.get("/")
# async def main_page() -> Response:
#     """_summary_

#     :return: _description_
#     :rtype: Response
#     """

#     return Response("hello, athlete. Welcome to your tracker!")


# @app.get("/dates")
# async def get_dates() -> list[str]:
#     """Returns a list of all workout dates in the table.

#     :return: _description_
#     :rtype: list[str]
#     """

#     return CRUD.read.get_dates(table)


# @app.get("/dates_and_splits")
# async def get_dates_and_splits() -> dict[str, list[str]]:
#     """_summary_

#     :return: dictionary of workout dates and their corresponding muscle groups
#     :rtype: dict[str, list[str]]
#     """

#     return CRUD.read.get_dates_and_muscle_groups(table)


# @app.get("/dates/{date}")
# async def describe_workout(date: str) -> HTTPException | dict:
#     """_summary_

#     :param date: _description_
#     :type date: str
#     :raises HTTPException: _description_
#     :return: dictionary describing the workout for the given date
#     :rtype: HTTPException | dict
#     """

#     if date not in CRUD.read.get_dates(table):
#         raise HTTPException(status_code=404, detail="Workout date not found")
#     return CRUD.read.describe_workout(table, date)


# @app.get("/{date}/exercises/{exercise}")
# async def show_exercise(exercise: str, date: str) -> list[str]:
#     """_summary_

#     :param exercise: _description_
#     :type exercise: str
#     :param date: _description_
#     :type date: str
#     :return: list of sets and reps for the given exercise and date
#     :rtype: list
#     """

#     return CRUD.read.show_exercise(table, exercise, date)


# if __name__ == "__main__":
#     uvicorn.run(app, port=8000, host="0.0.0.0")
