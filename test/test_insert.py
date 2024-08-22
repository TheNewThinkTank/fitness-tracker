
from tinydb import TinyDB

from test.conftest import src
from src.crud.insert import insert_log  # , insert_specific_log


def setup():
    test_db = TinyDB("test/test_db.json")
    test_table = test_db.table("test_log")
    return test_table


def test_insert_log():
    test_table = setup()

    log = "legs_training_log_2022-06-27.json"
    log_path = f"data/gustav_rasmussen/log_archive/JSON/2022/June/{log}"

    insert_log(test_table, log_path)

    # assert test_table.all() == open("test/sample.json", "r")

    # print(test_table.all())
    compare_file = TinyDB("test/sample.json").table("test_log").all()
    # print(compare_file)

    assert test_table.all() == compare_file
    teardown()


# def test_insert_specific_log():
#     ...


def teardown():
    # delete test_table
    test_table = setup()
    test_table.truncate()
