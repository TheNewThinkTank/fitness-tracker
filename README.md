![commit activity](https://img.shields.io/github/commit-activity/m/TheNewThinkTank/fitness-tracker)
![CI](https://github.com/TheNewThinkTank/fitness-tracker/actions/workflows/wf.yml/badge.svg)
[![GitHub repo size](https://img.shields.io/github/repo-size/TheNewThinkTank/fitness-tracker?style=flat&logo=github&logoColor=whitesmoke&label=Repo%20Size)](https://github.com/TheNewThinkTank/fitness-tracker/archive/refs/heads/main.zip)

[![Documentation Status](https://readthedocs.org/projects/fitness-tracker/badge/?version=latest)](https://fitness-tracker.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/TheNewThinkTank/Fitness-Tracker/branch/main/graph/badge.svg?token=CKAX4A3JQF)](https://codecov.io/gh/TheNewThinkTank/Fitness-Tracker)

# Fitness-Tracker

<p align="center">
<img src="https://lh3.googleusercontent.com/d/17ggezi9SP4a1_8GIzMJxV8b1VBbzhMFZ"width="400"/>
</p>

[Main Website](https://thenewthinktank.github.io/fitness-tracker/)

[Tech Docs](https://fitness-tracker.readthedocs.io/en/latest/index.html)

## Running locally

The default configuration reads year-based workout files from `data/`. Each file
must be named `<YEAR>_workouts.yml` and contain a TinyDB
`weight_training_log` table.

Environment variables are optional for the bundled data. Copy the template when
you need to point at another directory or protect direct API access:

```bash
cp .env.example .env
```

Supported variables:

| Variable | Description |
|---|---|
| `FITNESS_TRACKER_DATA_DIR` | Directory containing `<YEAR>_workouts.yml` files. Defaults to `data` |
| `FITNESS_TRACKER_ATHLETE` | Athlete label used by optional integrations. Defaults to `default` |
| `FITNESS_TRACKER_ALLOWED_ORIGINS` | JSON list of origins allowed to call FastAPI directly |
| `FITNESS_TRACKER_API_TOKEN` | Optional token required in the `X-API-Key` header |
| `FITNESS_TRACKER_STATE_DIR` | Writable SQLite directory; defaults to `DATA_DIR/.state` locally and `/state` in Compose |
| `FITNESS_TRACKER_ENABLE_WRITES` | Enable session-protected editing; defaults to `false` |
| `FITNESS_TRACKER_AUTH_REQUIRED` | Require athlete sign-in; a password must be provisioned first |
| `FITNESS_TRACKER_COOKIE_SECURE` | Require HTTPS and Secure cookies; enable behind a TLS reverse proxy |

### Docker Compose

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

The browser calls `/api` on the frontend origin. nginx forwards those requests
to FastAPI, so production browser traffic does not need CORS or a public backend
address. Compose mounts `data/` read-only and waits for backend readiness before
starting the frontend.

To enable token protection, set the same value for both services through the
Compose environment:

```bash
FITNESS_TRACKER_API_TOKEN="$(openssl rand -hex 32)" docker compose up --build
```

The token stays in nginx and FastAPI. It is not compiled into browser JavaScript.

### Analytics and editing

The frontend includes Archive, Progress, Programs, and Body Metrics views.
Progress covers the full selected date range across years, independently of
archive pagination. Exercise aliases are reviewed explicitly. Charts, personal
records, and calendar days link to source workouts, and program phases can be
overlaid on exercise history.

Metric definitions:

- Volume sums each set's `reps * load` and is reported in **kg-reps**, with known
	and unavailable load counts. Missing loads are not replaced with zero.
- `load_multiplier: 2` explicitly marks a per-hand load. Legacy dumbbell entries
	keep their recorded convention; the app never silently doubles them.
- Estimated 1RM uses Epley, Brzycki, or ACSM on positive external loads with
	1-10 reps. Recorded singles are unchanged. Bodyweight and band-assisted sets
	do not receive 1RM estimates; an estimate is not a measured maximum.
- Bodyweight loads use recorded workout mass or the most recent earlier
	measurement within 14 days, never future measurements or today's Google
	Sheets value. Bodyweight tonnage is a recorded-mass convention, not measured force.
- Holds, jump height, assistance, repetitions at a selected load, and relative
	strength have separate metrics. Exercise density divides selected sets by
	the entire timed session's minutes. Timing uses recorded clock windows.
- Missing measurements remain null. Unusual-estimate flags describe statistical
	variation, not injury risk or medical advice. Weekly activity starts on Monday
	and includes inactive weeks and distinct same-day sessions.
- Program completion compares logged and declared planned workouts. Rep-range
	adherence only counts sets with matching structured exercise/split targets.

Editing is opt-in and requires a password. Provision it interactively, then
restart the local API with editing enabled:

```bash
poetry run python -m src.utils.access_control --set-password
FITNESS_TRACKER_ENABLE_WRITES=true poetry run uvicorn src.main:app --reload
```

For Compose, provision the password in its persistent state volume:

```bash
docker compose run --rm backend python -m src.utils.access_control --set-password
FITNESS_TRACKER_ENABLE_WRITES=true docker compose up --build --detach
```

A provisioned password protects reads as well as writes. Sessions use revocable
HttpOnly, SameSite=Strict cookies; writes also require same-origin requests and
CSRF headers. Password changes revoke sessions. Before public exposure, set
`FITNESS_TRACKER_AUTH_REQUIRED=true` and `FITNESS_TRACKER_COOKIE_SECURE=true`
behind HTTPS. This is a single-athlete application, not a multi-user service.

Workout edits, deletions, measurements, and target overrides use transactional
SQLite, separate from read-only YAML archives. Stale `If-Match` versions return
`409`; missing versions return `428`. Do not edit the same imported records
concurrently through both the CLI and app. Back up YAML and SQLite state together;
stop the backend or use SQLite's backup API to copy an active database. Keep
the Compose `state` volume when preserving user data.

Workout JSON imports accept one object or a list of up to 1,000 workouts and
1 MiB. All rows validate before one transaction; supplied IDs and metadata are
preserved, and existing/duplicate IDs are rejected. Imports without IDs create
new workouts each time. CSV exports contain measurements, never credentials.

Body Metrics accepts manual entry or UTF-8 CSV:

```csv
date,weight_kg,waist_cm,resting_heart_rate
2026-10-01,80.5,85,60
2026-10-08,80.2,,58
```

Dates must be unique within a file. At most 10,000 rows and 1 MiB are accepted,
validated before any writes. Existing dates update in place; fields omitted from
the CSV retain their previous values. Explicit nulls in JSON can clear optional fields.

### Without containers

Requirements: Python 3.11 or 3.13, Poetry 2.2.1, and Node.js 24.

Start FastAPI:

```bash
poetry install --with analytics,integrations,docs
FITNESS_TRACKER_DATA_DIR=data poetry run uvicorn src.main:app --reload
```

Start Vite in another terminal:

```bash
cd frontend
npm ci
npm run dev
```

The development frontend runs at `http://localhost:5173` and proxies `/api` to
`http://localhost:8000`.

## API

The primary API endpoints are:

| Endpoint | Purpose |
|---|---|
| `GET /years` | List available imported archive and stored workout years |
| `GET /workouts` | Return a paginated year view with `asc` or `desc` ordering |
| `GET /workouts/{id}` | Return one workout and all exercise sets |
| `GET /healthz` | Report process liveness |
| `GET /readyz` | Confirm configured storage is available, including an empty new archive |
| `GET /exercises` | Canonical exercise names, aliases, dates, and muscle groups |
| `GET /analytics/overview` | Activity, known-load volume, timing, distributions, and prior-period comparisons |
| `GET /analytics/exercises/{id}` | Exercise history, selected `formula`, and optional `load_kg` filter |
| `GET /analytics/records` | Personal records linked to source workouts |
| `GET /analytics/export` | CSV matching applied date, exercise, formula, and load filters |
| `GET /programs` | Program history, structured targets, and observed adherence |
| `GET /body-metrics` | Historical weight, waist, and resting-heart-rate measurements |
| `GET /auth/status`, `POST /auth/login`, `POST /auth/logout` | Session status, sign-in, and revocation |
| `POST /workouts`, `PUT /workouts/{id}`, `DELETE /workouts/{id}` | Opt-in versioned workout editing |
| `POST /workouts/import` | Atomic workout JSON import |
| `POST /body-metrics`, `POST /body-metrics/import`, `DELETE /body-metrics/{date}` | Measurement entry, CSV import, and deletion |
| `PUT /programs/{id}/targets` | Persistent structured target overrides |

Analytics filters use `from=YYYY-MM-DD` and `to=YYYY-MM-DD`, with at most
ten years per request. `bucket` accepts `day`, `week`, or `month`.

`/data`, `/dates`, `/dates_and_splits`, and date-based detail routes remain
available as deprecated compatibility endpoints. Missing-year reads return
`404` and do not create files.

API records are cached in memory and indexed by workout ID. File identity,
size, and nanosecond modification/change timestamps invalidate changed
snapshots; replacing or deleting a year file does not require a server restart.
Anonymous reads retain the private, 60-second cache policy; session-protected
data uses `no-store`. Frontend requests bypass stale browser caches.

Generated OpenAPI files live in
`docs/project_docs/dev-docs/API-Schema/`. Regenerate them with:

```bash
poetry run ./bin/generate_openapi.sh
poetry run ./bin/generate_openapi.sh --check
```

## Workout data and identity

Imports and API responses share Pydantic validation. Dates must be valid
`YYYY-MM-DD` calendar dates. Exercise sets require an integer `set_number`,
integer `reps`, and string `weight`; additional workout and set metadata is
preserved. New invalid imports are rejected with the file path and validation
details. Invalid legacy rows are logged and omitted from API results.

Real-workout imports select the database for each requested date, including
comma-separated dates spanning multiple years:

```bash
poetry run python -m src.crud.insert --datatype real --dates 2022-02-08,2024-01-07
```

New workouts receive a stored UUID when written through configured workout
storage. IDs cannot be changed by updates and do not depend on reusable TinyDB
document numbers. The bundled records have been backfilled while preserving
their existing API URLs.

For an existing external data directory, back up the files and run the
idempotent migration from a writable environment before editing or renumbering
legacy records:

```bash
poetry run python -m src.utils.set_db_and_table --migrate-ids --dry-run
poetry run python -m src.utils.set_db_and_table --migrate-ids
```

Use `--year 2024` to limit migration or `--datatype simulated` for simulated
data. Unmigrated files remain readable through the legacy ID fallback, without
API reads modifying them. Keep a single writer for YAML data; atomic file
replacement does not provide multi-process transactions.

## Testing

```bash
# Backend
poetry run ruff check --config .config/ruff.toml src test
poetry run mypy --config-file .config/mypy.ini src --exclude '/site-packages/'
poetry run pytest test

# Frontend
npm --prefix frontend run check
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend audit --audit-level=moderate

# Browser workflows (install Chromium once)
npm exec --prefix frontend -- playwright install chromium
npm --prefix frontend run test:e2e
bats bin/test_fitcli.bats
```

With Compose running, set `E2E_BASE_URL=http://127.0.0.1:3000` for the browser
tests to include an unmocked frontend-to-backend workflow. CI runs these tests
against the production containers on desktop and mobile viewports.

CI then provisions a fixture-only password in disposable state, enables writes,
and runs authenticated browser workflows. For a separate disposable local stack,
use `E2E_WRITE_TESTS=1` and `--grep authenticated`; never point these write tests
at personal state. Use `E2E_PASSWORD` only for that test fixture's password.

## Container images

Two images are built, scanned, and published to GitHub Container Registry after
the Python and frontend CI jobs pass on `main`:

```
ghcr.io/thenewthinktank/fitness-tracker:latest
ghcr.io/thenewthinktank/fitness-tracker-frontend:latest
```

The backend image contains only API dependencies and bundled training metadata,
and runs one Uvicorn worker. SQLite state persists in `/state`; YAML remains
read-only. The frontend image contains
only nginx and the compiled static files. Both run as non-root users and include
health checks. Kubernetes deployments also need writable persistent state
owned by UID 10001; the rest of the filesystem can remain read-only.

Kubernetes deployment manifests and GitOps configuration live in the
[homelab](https://github.com/TheNewThinkTank/homelab) repository.

## For contributors

[Project tracking](https://thenewthinktank.atlassian.net/jira/software/projects/FT/boards/2)
