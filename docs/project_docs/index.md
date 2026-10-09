# Welcome

## Overview

Full stack fitness tracking application using TinyDB, SQLite, FastAPI, Svelte
and Docker. Imported weight-training records live in year-based
`<YEAR>_workouts.yml` files, each containing a TinyDB `weight_training_log`
table. FastAPI reads those archives without changing them. Optional frontend
workout entry and edits use transactional SQLite state, separate from YAML.

The browser opens the latest available year and supports date ordering,
pagination, and exercise-set details. Workouts have permanent UUIDs, so multiple
sessions on the same day remain distinct. Imports validate calendar dates and
record structure before writing; malformed legacy records are logged and
omitted from API results.

The API caches parsed records and indexes workout IDs. File identity, size, and
modification/change timestamps invalidate changed data without a server restart.
API reads do not modify the workout files. Anonymous responses use the private,
60-second cache policy; session-protected data uses `no-store`.

## Track and log workouts

- **Archive:** browse workouts by year, inspect sets, and edit or import records
    when authenticated writes are enabled.
- **Progress:** review full-range volume, activity, exercise history, personal
    records, and program phases; drill down to source workouts or export CSV.
- **Programs:** review dated programs and structured targets, with opt-in target
    editing.
- **Body Metrics:** view historical measurements, with opt-in manual entry and
    CSV import.

The header's **Log workout** action is available from every view. Enable writes,
provision an athlete password, and sign in before using it. Enter multiple
exercises and sets, plus optional times, gym, program, bodyweight, effort, and
notes. Successful saves open the new workout in Archive and preserve its link
after reload. See the [frontend guide](examples/svelte_frontend_setup.md)
for setup, validation rules, retry behavior, and storage details.

Most of the project, in particular `src` supports all major platforms (Windows, Linux and MacOS), but the cli `bin/fitcli.sh` currently supports Linux and MacOS only.

## Getting Started

Follow the [examples](examples/EXAMPLES.md) to install dependencies, import logs,
and run the application. For an existing data directory, follow the
[workout ID migration guide](examples/EXAMPLES.md#migrate-existing-workout-ids)
before editing or renumbering legacy records.

See the [browser workflow checks](examples/EXAMPLES.md#browser-workflow-checks)
for desktop and mobile testing, the
[architecture](architecture/architecture.md#application-runtime) for the
browser, archive, and writable-state boundaries, the
[OpenAPI reference](dev-docs/API-Schema/openapi.yaml) for the API contract, and
the [changelog](dev-docs/CHANGELOG.md#unreleased) for recent changes and
verification status.

## References

The development and concepts behind this fitness tracker are influenced by the following references:

### Book

The book "Exercise Physiology: Nutrition, Energy, and Human Performance" provides detailed information on exercise physiology,
nutrition, energy, and human performance, which, together with other textbooks and articles,
form the foundation of the algorithms and recommendations used in this application.

### Education

My formal education as both a fitness instructor at the "At Work" school as well as a Running Coach at the "DGI" school
has provided me with the theoretical and practical knowledge necessary to design effective fitness programs and tracking systems.
In addition, I hold the instructor certificate in Leung Ting Wing Tsun from "Wing Tsun Instructor Academy"
which besides main focus on this discipline, incorporated elements of strength and cardio training, nutrition, yoga and more.

### Professional Experience

My hands-on experience working as a fitness instructor at SATS for two years has given me valuable insights into
the practical aspects of fitness training and client management.
This experience has been instrumental in shaping the user experience and functionality of this application.
I furthermore had the priveledge to teach classes at various martial arts gyms across different styles, across greater Copenhagen
for a number of years.

!!! tip "Similar projects"
    If you liked this fitness tracker then you might also be interested in
    the [workout-generator](https://github.com/TheNewThinkTank/workout-generator) Django project,<br>
    the [nutrition-planner](https://github.com/TheNewThinkTank/nutrition-planner) Streamlit project, with associated development guide:<br>
    [medium](https://medium.com/@GustavCollinRasmussen/build-a-nutrition-app-on-streamlit-8c4f01229989),<br>
    the [athlete](https://github.com/TheNewThinkTank/athlete) project,<br>
    or the [Dojo](https://gitlab.com/sports-tracking/dojo) martial arts project
    which can be found on GitLab and is a Rust & TypeScript based general purpose martial arts desktop application
