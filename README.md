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

The primary read endpoints are:

| Endpoint | Purpose |
|---|---|
| `GET /years` | List years that have an existing workout database |
| `GET /workouts` | Return a paginated year view with `asc` or `desc` ordering |
| `GET /workouts/{id}` | Return one workout and all exercise sets |
| `GET /healthz` | Report process liveness |
| `GET /readyz` | Confirm that at least one workout database can be read |

`/data`, `/dates`, `/dates_and_splits`, and date-based detail routes remain
available as deprecated compatibility endpoints. Missing-year reads return
`404` and do not create files.

API records are cached in memory and indexed by workout ID. File identity,
size, and nanosecond modification/change timestamps invalidate changed
snapshots; replacing or deleting a year file does not require a server restart.
HTTP responses retain the existing private, 60-second browser cache policy.

Generated OpenAPI files live in
`docs/project_docs/dev-docs/API-Schema/`. Regenerate them with:

```bash
poetry run ./bin/generate_openapi.sh
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
poetry run ruff check src test
poetry run mypy src --exclude '/site-packages/'
poetry run pytest test

# Frontend
npm --prefix frontend run check
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend audit --audit-level=moderate

# Browser workflows (install Chromium once)
npm exec --prefix frontend -- playwright install chromium
npm --prefix frontend run test:e2e
```

With Compose running, set `E2E_BASE_URL=http://127.0.0.1:3000` for the browser
tests to include an unmocked frontend-to-backend workflow. CI runs these tests
against the production containers on desktop and mobile viewports.

## Container images

Two images are built, scanned, and published to GitHub Container Registry after
the Python and frontend CI jobs pass on `main`:

```
ghcr.io/thenewthinktank/fitness-tracker:latest
ghcr.io/thenewthinktank/fitness-tracker-frontend:latest
```

The backend image contains only API dependencies and runs one Uvicorn worker,
which matches the YAML storage concurrency model. The frontend image contains
only nginx and the compiled static files. Both run as non-root users and include
health checks.

Kubernetes deployment manifests and GitOps configuration live in the
[homelab](https://github.com/TheNewThinkTank/homelab) repository.

## For contributors

[Project tracking](https://thenewthinktank.atlassian.net/jira/software/projects/FT/boards/2)
