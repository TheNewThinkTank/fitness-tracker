"""_summary_
"""

import json

from behave import Given, When, Then

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.helpers.validate import Workout


@Given("A JSON file with test data")
def given_combo(context):
    context.file = "features/steps/test_data_validate.json"


@When("Reading the file content")
def when_lookup(context):
    with open(context.file) as rf:
        context.data = json.load(rf)["weight_training_log"]


@Then("It should conform to the pydantic Workout class validation")
def then_results(context):
    workouts: list[Workout] = [Workout(**item) for item in context.data.values()]
    assert isinstance(type(workouts[0].exercises), dict)
