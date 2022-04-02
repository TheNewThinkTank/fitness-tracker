"""
Date: 2021-12-11
Author: Gustav Collin Rasmussen
Purpose: Expose API for training data

Doc: https://fastapi.tiangolo.com/tutorial/first-steps/

To run, execute following command from CLI:
cd src && uvicorn main:app --reload

visit URL: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI  # type: ignore
import json
from tinydb import TinyDB  # type: ignore

from CRUD.training import describe_workout, show_exercise  # type: ignore

app = FastAPI()

datatype = "real"

data = json.load(open(file="./config.json", encoding="utf-8"))
db = (
    TinyDB(data["real_workout_database"])
    if datatype == "real"
    else TinyDB(data["simulated_workout_database"])
)
table = (
    db.table(data["real_weight_table"])
    if datatype == "real"
    else db.table(data["simulated_weight_table"])
)

# db = TinyDB("../data/db.json")
# log = db.table("log")


@app.get("/dates/{date}")
async def get_workout_description(date: str):
    return describe_workout(table, date)


@app.get("/{date}/exercises/{exercise}")
async def get_exercise_info(exercise: str, date: str):
    return show_exercise(table, exercise, date)
