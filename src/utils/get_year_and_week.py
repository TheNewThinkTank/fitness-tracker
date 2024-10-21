"""_summary_
"""

import datetime


def get_year_and_week(date_str):
    """_summary_

    :param date_str: _description_
    :type date_str: _type_
    :return: _description_
    :rtype: _type_
    """

    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    year_week_str = dt.date().strftime("%Y %U")
    year = year_week_str.split(" ")[0]
    week = "01" if (w := year_week_str.split(" ")[1]) == "00" else w
    week = int(week.removeprefix("0"))

    return year, week


def main():
    """_summary_
    """

    test_dates = ["2022-10-29", "2022-10-30", "2021-01-01"]
    date_str = test_dates[-1]
    year, week = get_year_and_week(date_str)
    print(year, week)

    # TESTING
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    year, week, day_of_week = dt.isocalendar()
    print(year, week, day_of_week)


if __name__ == "__main__":
    main()
