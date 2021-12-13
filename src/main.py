"""
Date: 2021-12-11
Author: Gustav Collin Rasmussen
Purpose: Expose API for training data

Doc: https://fastapi.tiangolo.com/tutorial/first-steps/

To run, execute following command from CLI:
cd src && uvicorn main:app --reload

visit URL: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from tinydb import TinyDB

from training import describe_workout, show_exercise

app = FastAPI()

db = TinyDB("../data/db.json")
log = db.table("log")


# @app.get("/")
# async def root():
#     date = "2021-12-13"
#     return describe_workout(log, date)  # , show_exercise(log, "squat", date)


@app.get("/dates/{date}")
async def describe_workout(date: str):
    return describe_workout(log, date)


@app.get("/{date}/exercises/{exercise}")
async def show_exercise(exercise: str, date: str):
    return show_exercise(log, exercise, date)
