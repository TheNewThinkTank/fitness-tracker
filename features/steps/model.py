from behave import Given, When, Then

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.model.model import get_df  # get_data, one_rep_max_estimator
from src.utils.set_db_and_table import set_db_and_table  # type: ignore

db, table, _ = set_db_and_table(datatype="real", athlete="gustav_rasmussen")


@Given("A valid combination of musclegroup and exercise")
def given_combo(context):
    context.combo = ("legs", "squat")
    # TODO: check combo exists in catalog


@When("Looking up in the db")
def when_lookup(context):
    split, ex = context.combo
    context.get_df = get_df(table, split, ex)


@Then("The resulting dataframe has more than 2 entries")
def then_results(context):
    assert len(context.get_df) > 2
