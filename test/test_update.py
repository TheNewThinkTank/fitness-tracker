
from tinydb import TinyDB

from context import src
from src.crud.update import update_table, remove_from_table, truncate_table


def setup():
    MOCK_DB = TinyDB("test/test_db.json")
    test_table = MOCK_DB.table("test_log")
    return test_table


def test_update_table():
    # TODO: assert update
    test_table = setup()
    update_table(test_table)
    # assert
    # teardown()


def test_remove_from_table():
    # TODO: assert removal
    test_table = setup()
    remove_from_table(test_table)


def test_truncate_table():
    test_table = setup()
    truncate_table(test_table)
    assert test_table.all() == []


def teardown():
    ...
