"""Delete data from the database.
"""

from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def remove_from_table(table):
    """Remove from table.

    :param table: TinyDB table
    :type table: TinyDB.table
    """

    # Workout = Query()
    # table.remove(Workout.exercises.squat < 5)

    return NotImplementedError


def truncate_table(table) -> None:
    """Truncate table.

    :param table: TinyDB table
    :type table: TinyDB.table
    """

    table.truncate()


def main() -> None:
    """Main function.
    """

    datamodels = ["real", "simulated"]
    datatype = datamodels[0]

    db, table, _ = set_db_and_table(
        datatype,
        env="dev"
        )

    # ic(db)
    # ic(table)
    # all_entries = table.all()
    # ic(all_entries)

    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
