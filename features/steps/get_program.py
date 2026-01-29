from behave import Given, When, Then

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.utils.get_program import get_pgm_from_date


@Given("A valid workout-date string")
def given_date(context):
    dates = ["2022-01-01", "2022-04-01", "2022-07-01"]
    context.date0 = dates[0]
    context.date1 = dates[1]
    context.date2 = dates[2]


@When("Fetching the program name")
def when_lookup(context):
    context.pgm0 = get_pgm_from_date(context.date0)
    context.pgm1 = get_pgm_from_date(context.date1)
    context.pgm2 = get_pgm_from_date(context.date2)


@Then("The program name must have the right value")
def then_results(context):
    assert context.pgm0 == "4-SPLIT"
    assert context.pgm1 == "PPL"
    assert context.pgm2 == "GVT"
