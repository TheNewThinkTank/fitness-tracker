"""
Date: 2021-12-11
Author: Gustav Collin Rasmussen
Purpose: Expose API for training data

Doc: https://fastapi.tiangolo.com/tutorial/first-steps/

To run, execute following command from CLI:
uvicorn main:app --reload

visit URL: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from tinydb import TinyDB

from training import describe_workout, show_exercise

app = FastAPI()

db = TinyDB("db.json")
log = db.table("log")


@app.get("/")
async def root():
    return describe_workout(log), show_exercise(log, "squat")


@app.get("/exercises/{exercise}")
async def read_item(exercise: str):
    return show_exercise(log, exercise)
