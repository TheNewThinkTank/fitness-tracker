import glob
import sys
import os

from pathlib import Path

from behave import Given, When, Then

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.utils.lookup import get_year_and_month


@Given("A valid workout-date as string")
def given_date(context):
    dates = ["2021-12-10", "2022-06-27"]
    context.date = dates[1]


@When("Extracting the year and month")
def when_lookup(context):
    context.YEAR, context.MONTH = get_year_and_month(context.date)


@Then("The corresponding training log exists")
def then_results(context):

    athlete = "gustav_rasmussen"

    log_path = glob.glob(
        f"data/{athlete}/log_archive/JSON/{context.YEAR}/{context.MONTH}/*training_log_{context.date}.json"
    )
    if log_path:
        path = Path(log_path[0])
        assert path.is_file()
    else:
        raise ValueError
