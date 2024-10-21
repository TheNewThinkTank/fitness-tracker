"""
Date: 2022-07-01
Purpose: Update or delete weight-training data
"""

import os
from pprint import pprint as pp
import re
import sys
from icecream import ic  # type: ignore
# from tinydb import Query, where  # type: ignore
from tinydb import Query  # type: ignore
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from utils.set_db_and_table import set_db_and_table  # type: ignore


def filter_exercises_with_whitespace(workout_data):
    """Find exercises with whitespace.

    :param workout_data: _description_
    :type workout_data: _type_
    :return: _description_
    :rtype: _type_
    """
    filtered_exercises = []
    for workout in workout_data:
        exercises_with_whitespace = [
            exercise for exercise in workout['exercises'].keys() if ' ' in exercise
        ]

        # If any exercise with whitespace is found, add the workout to the result
        if exercises_with_whitespace:
            filtered_exercises.append({
                'date': workout['date'],
                'split': workout['split'],
                'exercises_with_whitespace': exercises_with_whitespace
            })

    return filtered_exercises


def clean_exercise_names(table) -> None:
    workout_data = table.all()
    for workout in workout_data:
        new_exercises = {}
        for exercise in workout['exercises']:
            # Replace spaces with underscores if there isn't an underscore before or after
            cleaned_exercise_name = re.sub(r'(?<!_) (?!_)', '_', exercise)
            # If there is an underscore before or after, remove the space
            cleaned_exercise_name = re.sub(r'(?<=_) | |(?=_)', '', cleaned_exercise_name)

            new_exercises[cleaned_exercise_name] = workout['exercises'][exercise]
        workout['exercises'] = new_exercises

        table.update(workout, Query().date == workout['date'])


def main() -> None:
    """_summary_"""

    datamodels = ["real", "simulated"]
    datatype = datamodels[0]

    db, table, _ = set_db_and_table(
        datatype,
        env="dev"
        )

    # workout_data = table.all()
    # pp(workout_data)
    # pp(filter_exercises_with_whitespace(workout_data))
    # print("##########")
    clean_exercise_names(table)
    # print("##########")
    # pp(filter_exercises_with_whitespace(workout_data))

    # ic(db)
    # ic(table)
    # all_entries = table.all()
    # ic(all_entries)

    # remove_from_table(table)
    # truncate_table(table)


if __name__ == "__main__":
    main()
