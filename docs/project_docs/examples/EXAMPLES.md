# Examples

## Getting started

First, clone the project:<br>
`git clone https://github.com/TheNewThinkTank/fitness-tracker.git`

Run the commands below from the repository root. Use Python 3.11 or 3.13,
Poetry 2.2.1, and Node.js 24 or newer for the frontend.

```bash
poetry install --with analytics,integrations,docs
```

### Import workout logs

Place one workout per archive file under the configured `FITNESS_TRACKER_DATA_DIR`
(the default is `data/`). For example:

```text
data/log_archive/YML/2024/January/training_log_2024-01-07.yml
```

The file can contain:

```yaml
date: '2024-01-07'
start_time: '09:00'
end_time: '10:00'
timezone: CET
split: push
exercises: {bench_press: [{set_number: 1, reps: 8, weight: '40 kg'}]}
```

Dates must be real calendar dates in `YYYY-MM-DD` format and match the requested
archive date. Each exercise set requires integer `set_number` and `reps` fields
and a string `weight`. Additional workout and set metadata is preserved. Omit
`id` for a new workout; configured storage assigns a permanent UUID when writing.

Import the log with:

```bash
poetry run python -m src.crud.insert --datatype real --dates 2024-01-07 --file_format yml
```

This writes to `data/2024_workouts.yml`, not the current calendar year's file.
To import across years, first prepare both archive files, including
`data/log_archive/YML/2022/February/training_log_2022-02-08.yml`, then run:

```bash
poetry run python -m src.crud.insert --datatype real --dates 2022-02-08,2024-01-07 --file_format yml
```

The importer selects a separate database for each date's year. For a second
workout on the same day, use a filename such as `training_log_2024-01-07_2.yml`:

```bash
poetry run python -m src.crud.insert --datatype real --dates 2024-01-07 --workout_number 2
```

JSON logs use the same record structure under `log_archive/JSON/<YEAR>/<Month>/`
with a `.json` extension and `--file_format json`. Imports append records;
repeating an import can create another workout. Use a separate data directory
when experimenting with the examples.

## Migrate existing workout IDs

The 253 bundled workouts have been backfilled with permanent IDs while retaining
their existing API URLs. For an external legacy data directory, back up its
files and stop other writers before migrating. Set `FITNESS_TRACKER_DATA_DIR`
to that directory, then preview and apply the migration:

```bash
poetry run python -m src.utils.set_db_and_table --migrate-ids --dry-run
poetry run python -m src.utils.set_db_and_table --migrate-ids
```

Limit the operation to one year when needed:

```bash
poetry run python -m src.utils.set_db_and_table --migrate-ids --year 2024
```

Use `--datatype simulated` to migrate the configured simulated database. The
migration preserves existing fields and legacy URLs; running it again makes no
changes once IDs are present. Preserve these IDs when moving or editing records.

Unmigrated files remain readable through the legacy ID fallback, but migrate them
before editing or renumbering their TinyDB documents. API reads never backfill
files, and Compose mounts workout data read-only. Run migrations from a writable
environment with a single writer: atomic YAML replacement is not a multi-process
transaction mechanism.

## Running locally

The bundled `data/` directory works without environment variables. Copy the
template only when using another data directory or an API token:

```bash
cp .env.example .env
```

### With Docker Compose

```bash
docker compose up --build
```

- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

### Without containers

```bash
# Start the backend
FITNESS_TRACKER_DATA_DIR=data poetry run uvicorn src.main:app --reload

# Start the frontend (separate terminal)
npm --prefix frontend ci
npm --prefix frontend run dev
```

The development frontend is available at `http://localhost:5173` and proxies API
requests to port 8000.

## Testing endpoints locally

Overview of endpoints:

- [root](http://127.0.0.1:8000/)
- [years](http://127.0.0.1:8000/years)
- [workouts](http://127.0.0.1:8000/workouts?year=2024&limit=25&order=desc)
- Workout detail: `GET /workouts/{workout_id}`, using an item's `id` from `/workouts`
- [healthz](http://127.0.0.1:8000/healthz)
- [readyz](http://127.0.0.1:8000/readyz)

The list endpoint defaults to the latest available year. A missing year returns
`404` without creating a file. Select individual workouts by UUID rather than
date, since two workouts can share a date. When an API token is configured,
direct backend requests need `X-API-Key`; the same-origin frontend proxy adds
the token server-side.

## Browser workflow checks

Install frontend dependencies and Chromium, then run the checks:

```bash
npm --prefix frontend ci
npm exec --prefix frontend -- playwright install chromium
npm --prefix frontend run check
npm --prefix frontend test
npm --prefix frontend run test:e2e
```

Playwright builds the frontend and starts an isolated preview on port 4173; set
`E2E_PORT` to choose another port. Deterministic API fixtures exercise year
selection, pagination, ordering, duplicate-day details, and error/retry behavior
on desktop and mobile viewports. The unmocked integration test is skipped unless
`E2E_BASE_URL` points to a running application.

For a running Compose stack:

```bash
E2E_BASE_URL=http://127.0.0.1:3000 npm --prefix frontend run test:e2e
```

For a local Vite proxy, use its URL instead (normally `http://127.0.0.1:5173`).
The container CI job is configured to run the browser suite against the built
Compose services and retain failure screenshots and traces in the
`browser-test-results` artifact. See the
[verification status](../dev-docs/CHANGELOG.md#verification-status) for the
checks performed locally and the outstanding container runtime verification.

## Example: insert breath holding data in TinyDB

```bash
python3 src/utils/get_breath_holding.py

./bin/fitcli.sh
./bin/fitcli.sh -d 2024-03-03 -f json
```
