"""
_summary_
"""

import datetime
from datetime import datetime as dt
import yaml  # type: ignore
from config_loader import ConfigLoader  # type: ignore
from profiling_tools.profiling_utils import profile  # type: ignore
from datetime_tools.get_duration import get_duration_minutes  # type: ignore


def get_data(year):
    """_summary_

    :param year: _description_
    :type year: _type_
    :return: _description_
    :rtype: _type_
    """
    config = ConfigLoader.load_config()
    file = config["real_workout_database"].replace("<YEAR>", year)
    with open(file) as rf:
        data = yaml.safe_load(rf)["weight_training_log"]

    return data


@profile
def get_all_durations(year):
    """_summary_

    :return: _description_
    :rtype: _type_
    """

    data = get_data(year)

    date_and_duration = {}
    for workout_number in data:
        if "start_time" in data[workout_number]:
            date = data[workout_number]["date"]
            start_time = data[workout_number]["start_time"]
            end_time = data[workout_number]["end_time"]

            duration = get_duration_minutes(start_time, end_time)
            # timezone = data[workout_number]["timezone"]

            date_and_duration[date] = duration

    # pp(date_and_duration)

    return date_and_duration


def main():
    """_summary_
    """

    year = str(dt.now().year)
    date_and_duration = get_all_durations(year)
    for date, duration in date_and_duration.items():
        print(date, duration)


if __name__ == "__main__":
    main()
