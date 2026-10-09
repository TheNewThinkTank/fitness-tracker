# Frontend setup

The existing frontend uses Svelte 5, TypeScript, Vite, and Zod. It provides
Archive, Progress, Programs, and Body Metrics views, with workout entry
available from every view. Charts and the workout editor load on demand.

Run the commands below from the repository root with Node.js 24 or newer.
For backend dependencies and environment settings, see
[getting started](EXAMPLES.md#getting-started).

## Start the application

For the production containers:

```bash
docker compose up --build
```

Open `http://localhost:3000`. For development, start FastAPI and Vite in separate
terminals:

```bash
FITNESS_TRACKER_DATA_DIR=data poetry run uvicorn src.main:app --reload

# In a separate terminal
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open `http://localhost:5173`. The browser uses relative `/api` routes; Vite and
production Nginx forward requests to FastAPI on the browser's behalf. If the
backend requires `FITNESS_TRACKER_API_TOKEN`, pass the same server-side value
to the frontend proxy. Never put the service token in browser code.

## Enable workout entry

Writes are disabled by default. Provision an athlete password before starting
the backend with `FITNESS_TRACKER_ENABLE_WRITES=true`.

For a local API:

```bash
poetry run python -m src.utils.access_control --set-password
FITNESS_TRACKER_ENABLE_WRITES=true poetry run uvicorn src.main:app --reload
```

For Compose, provision the password in the persistent state volume:

```bash
docker compose run --rm backend python -m src.utils.access_control --set-password
FITNESS_TRACKER_ENABLE_WRITES=true docker compose up --build --detach
```

A provisioned password protects reads as well as writes. Sign in in the
frontend; the **Log workout** action stays disabled until writes are enabled
and the athlete is authenticated. Sessions use HttpOnly, SameSite=Strict
cookies, and writes require same-origin requests plus a session CSRF header.
Use HTTPS and `FITNESS_TRACKER_COOKIE_SECURE=true` for public deployments.

## Log a workout

1. Select **Log workout** in the header from Archive, Progress, Programs,
	or Body Metrics.
2. Set the date and split. The date defaults to your local calendar date,
	not the UTC date.
3. Enter an exercise identifier from the catalog, then its repetitions and
	load. Use **Add set** or **Add exercise** for additional entries. Exercise
	names must be distinct; names are saved in lowercase and sets are renumbered
	after removals. At least one exercise and one set must remain.
4. Optionally record start/end times, gym, program, bodyweight, session RPE,
	reps in reserve, notes, hold duration, height, or a per-hand load.
5. Select **Save workout**. Archive opens the saved workout and selects its
	year, including a year with no imported YAML file. Reloading its URL retains
	the selected year and detail.

Provide both times or leave both blank. Overnight sessions are allowed, but
the time window must be greater than zero and at most 12 hours. **Per hand**
explicitly doubles that set's recorded load for volume calculations; it is not
inferred from an exercise name. The editor accepts up to 100 exercises and
100 sets per exercise. Optional effort fields do not change the recorded
repetitions or load.

Controls and dismissal are locked while a save is pending. Validation failures
and retryable server errors keep the entered draft for correction or retry.
An expired session returns to sign-in; authenticate again before entering a
workout. Notes are displayed as text, not interpreted as HTML.

## Storage and edits

New workouts receive permanent UUIDs and are stored in transactional SQLite,
separate from the imported year-based YAML archives. Logging a workout through
the frontend does not rewrite those archives. Compose persists SQLite in its
`state` volume; preserve that volume and back up both storage sources.

Updates retain the workout ID and send the current version with `If-Match`.
A stale version returns `409`; a missing version returns `428`. Deletes require
confirmation. Editing an existing workout from Progress keeps that view active;
creating a new workout returns to Archive.

## Check the frontend

```bash
npm --prefix frontend run check
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend audit --audit-level=moderate
npm --prefix frontend run test:e2e
```

Install Playwright's Chromium before the first browser run. See
[browser workflow checks](EXAMPLES.md#browser-workflow-checks) for deterministic
and real-backend desktop/mobile tests. Authenticated tests must use disposable
state and a fixture-only password, never personal workout state.
