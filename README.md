# Fitness-Tracker

Full stack fitness tracking application using TinyDB and FastAPI.
Add weight-training logs continuously to db.json and query the data through the browser.
Visually inspect your progression through dates and exercises

![fitness-tracker-wf](https://github.com/TheNewThinkTank/Fitness-Tracker/actions/workflows/fitness-tracker-wf.yml/badge.svg)

![alt](img/workout_2021-12-11.png)

Above: selected exercises (sets vs reps, with weight resistance shown in the legend) for leg workout on 2021-12-11

## Current features

- Test suite (Pytest)
- Plotting (Seaborn)
- GitHub Actions workflow

## Upcoming features

- Data simulation (Faker)
- Documentation (Sphinx)
- Bodily strength-ratio tracking (determine baseline, ideal-ranges, and compare the two)
- YAML-support
- Add cardio tracking (integrate app with Strava)
- Dashboard
- Add key exercises (benchpress, squat, deadlift) to dashboard
- Hosting on PyPi
