
from tinydb import TinyDB

import pytest

from test.conftest import src

pytestmark = pytest.mark.skip(reason="Skip until ModuleNotFoundError is fixed")

search_table = pytest.importorskip("src.crud.update.search_table")
remove_from_table = pytest.importorskip("src.crud.update.remove_from_table")
truncate_table = pytest.importorskip("src.crud.update.truncate_table")

# from src.crud.update import search_table, remove_from_table, truncate_table


def setup():
    MOCK_DB = TinyDB("test/test_db.json")
    test_table = MOCK_DB.table("test_log")
    return test_table


@pytest.mark.skip(reason="Skip until ModuleNotFoundError is fixed")
def test_search_table():
    # TODO: assert update
    test_table = setup()
    search_table(test_table)
    # assert
    # teardown()


@pytest.mark.skip(reason="Skip until ModuleNotFoundError is fixed")
def test_remove_from_table():
    # TODO: assert removal
    test_table = setup()
    remove_from_table(test_table)


@pytest.mark.skip(reason="Skip until ModuleNotFoundError is fixed")
def test_truncate_table():
    test_table = setup()
    truncate_table(test_table)
    assert test_table.all() == []


def teardown():
    ...
