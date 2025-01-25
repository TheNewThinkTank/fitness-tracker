"""_summary_
"""

import pytest
from tinydb import TinyDB
# from datetime_tools.lookup import Months  # type: ignore
# from src.utils.config_loader import ConfigLoader  # type: ignore
from src.utils.custom_storage import YAMLStorage  # type: ignore
from src.crud.insert import (  # type: ignore
    insert_log,
    # insert_all_logs,
    # insert_specific_log
    )

# env_vars = ConfigLoader.load_env_variables()
# config = ConfigLoader.load_config()
# base_path = config["google_drive_data_path"]

# year, month_zeropadded, day = "2022", "06", "27"
# # TODO: move to datetime_tools.lookup
# month = int(month_zeropadded.removeprefix("0"))
# month_name = Months(month).name.capitalize()

log = "workout_sample_data.yml"
log_path = "docs/project_docs/examples/workout_sample_data.yml"


def setup():
    test_db = TinyDB("test/test_db.yml", storage=YAMLStorage)
    test_table = test_db.table("test_log")
    # TODO: fetch workout log from Google Drive here
    return test_table


@pytest.mark.skip(reason="Skip until getting log from Google Drive is implemented.")
def test_insert_log():
    test_table = setup()

    # log = f"legs_training_log_{year}-{month_zeropadded}-{day}.json"
    # log_path = f"data/{env_vars['ATHLETE']}/log_archive/JSON/{year}/{month_name}/{log}"
    file_format = log.split(".")[-1]

    insert_log(test_table, log_path, file_format)

    # assert test_table.all() == open("test/sample.json", "r")

    # print(test_table.all())
    compare_file = TinyDB("test/test_db.yml").table("test_log").all()
    # print(compare_file)

    assert test_table.all() == compare_file
    teardown()


# def test_insert_specific_log():
#     ...


def teardown():
    # delete test_table
    test_table = setup()
    test_table.truncate()
