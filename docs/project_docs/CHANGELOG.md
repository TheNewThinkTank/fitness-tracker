# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Fix OpenAPI wf
- add quantitative flexibility measurements / estimations
- quality control for TS and JS
- timezone check; check stated timezone in workout logs are consistent with the definition:
      CEST spans from the last Sunday in March to the last Sunday in October.
      start by checking that workout logs timezone data for November -> February are not CEST
- download db.yml and run python analysis and plotting code on it,
    using: [interact-with-google-drive](https://github.com/marketplace/actions/interact-with-google-drive)
- deploy and host containerized app on Raspberry Pi
- Add muscle groups to log file name
- ML models (Scikit Learn)
- Bodily strength-ratio tracking (determine baseline, ideal-ranges, and compare the two)
- Dashboard
- Add key exercises (benchpress, squat, deadlift) to dashboard
- Hosting on PyPi (automated deploy with GitHub Actions)
- Identify musclegroups and exercises with best or worst progression
- Add cardio tracking (integrate app with Strava)

<!--
### Changed
### Removed
### Fixed

## [0.0.2] - YYYY-MM-DD

### Added

- src/helpers/google_sheets module for interacting with google sheets

### Changed

- src/helpers/get_bodyweight.py: uses new google_sheets module

-->

## [0.0.1] - 2024-08-17

### Added

- This CHANGELOG file
- FastAPI app "Fitness-Tracker", with TinyDB backend, exposed through Docker container
- Program logging (Located in folder: logs)
- Plotting with the Seaborn library
- Tech Docs, auto-generated by Sphinx and hosted on readthedocs
- Multiple unit test suites (Pytest)
- BDD (Behavior Driven Development, using the Behave framework)
- Multiple GitHub Actions workflows
- Data quality validation (Pydantic, Great Expections)
- Package dependency management (Poetry)
- KPI tracking: 1-Rep-Max estimation (Epley and Brzycki formulas)
- Realistic workout data simulation (with naturally progressing trend over time)
- Catalogue of musclegroups, corresponding exercises and suggested weight ranges (for simulations)

<!--
[unreleased]:
-->