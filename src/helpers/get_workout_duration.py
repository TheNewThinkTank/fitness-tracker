import cProfile
import datetime
from datetime import datetime as dt
import json

# from pprint import pprint as pp

DATA = json.load(open(file="./config.json", encoding="utf-8"))
file = DATA["real_workout_database"].replace("<ATHLETE>", "gustav_rasmussen")
with open(file) as rf:
    data = json.load(rf)["weight_training_log"]


def get_workout_duration(start_time, end_time):
    start_time_object = dt.strptime(start_time, "%H:%M")
    end_time_object = dt.strptime(end_time, "%H:%M")

    duration = end_time_object - start_time_object
    duration_minutes = round(duration / datetime.timedelta(minutes=1))

    return duration_minutes


def get_all_durations():
    date_and_duration = {}

    for workout_number in data:
        if "start_time" in data[workout_number]:
            date = data[workout_number]["date"]
            start_time = data[workout_number]["start_time"]
            end_time = data[workout_number]["end_time"]

            duration = get_workout_duration(start_time, end_time)
            # timezone = data[workout_number]["timezone"]

            date_and_duration[date] = duration

    return date_and_duration


def main():
    profiler = cProfile.Profile()
    profiler.enable()

    date_and_duration = get_all_durations()

    for date, duration in date_and_duration.items():
        print(date, duration)

    profiler.disable()
    profiler.dump_stats("stats/get_workout_duration.stats")


if __name__ == "__main__":
    main()
