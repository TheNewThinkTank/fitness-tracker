# Fitness Tracker frontend

The frontend is a Svelte 5 and TypeScript application built with Vite. It loads
available years, paginated workout summaries, and exercise details from relative
`/api` routes.

## Views

- **Archive:** workout paging and detail, plus opt-in logging, version-aware
	editing/deletion, and JSON import.
- **Progress:** full-range analytics, exercise and constant-load filters,
	formula selection, program-phase overlays, comparisons, personal records,
	an activity calendar, source-workout drill-down, and CSV export.
- **Programs:** dated history, planned/recorded workouts, checked rep-range
	adherence, and structured target editing.
- **Body Metrics:** historical weight, waist, and resting-heart-rate charts,
	manual entry, CSV import/export, and confirmed deletion.

Chart and editor modules load on demand. Zod validates numeric responses before
they reach ECharts; missing values remain null. Tooltips use canvas rich text,
and tables remain available alongside charts. Date/exercise/formula filters and
workout links are encoded in the URL.

Editing requires the backend's athlete password and
`FITNESS_TRACKER_ENABLE_WRITES=true`. Provisioning and HTTPS configuration are
documented in the [project README](../README.md#analytics-and-editing).
Sessions use HttpOnly cookies and in-memory CSRF headers, never localStorage
credentials or browser-side service keys.

## Log a workout

The header's **Log workout** action is available from every view. It remains
disabled on read-only servers or until the athlete signs in. The editor starts
with the athlete's local date and a blank exercise name, supports multiple
exercises and sets, and accepts optional times, gym, program, bodyweight, effort,
hold duration, height, per-hand loads, and notes.

Workout writes are checked against the backend's date, time-window, metadata,
and set limits before submission. Times must be provided together; overnight
sessions are supported. Controls are locked during a save, and failed requests
retain the draft for correction or retry. A successful insert selects the saved
year in Archive, opens the new workout, and keeps the link usable after reload.

## Development

Use Node.js 24 or newer. Start the FastAPI service on port 8000, then run:

```bash
npm ci
npm run dev
```

Vite listens on `http://localhost:5173` and proxies `/api` to
`http://localhost:8000`. Override the target when needed:

```bash
VITE_API_PROXY_TARGET=http://localhost:9000 npm run dev
```

If FastAPI requires `FITNESS_TRACKER_API_TOKEN`, pass the same server-side value
to Vite. The proxy adds the `X-API-Key` header without exposing the token to
browser code:

```bash
FITNESS_TRACKER_API_TOKEN=local-token npm run dev
```

## Quality checks

```bash
npm run check
npm test
npm run build
npm audit --audit-level=moderate
```

`npm run check` covers Svelte and TypeScript diagnostics. Vitest covers API URL
construction, workout input constraints, authenticated POST payloads,
version-aware updates, error handling, response validation, and server rendering.

### Browser workflows

Install Chromium once, then run Playwright on desktop and mobile viewports:

```bash
npx playwright install chromium
npm run test:e2e
```

Playwright builds the frontend and starts an isolated preview on port 4173.
Set `E2E_PORT` to use another port. Deterministic API fixtures cover year
selection, pagination, duplicate-day details, error/retry behavior, complete
progress totals, selected calendar years, chart pixels, CSV export, and
program/body navigation. Workout insertion tests cover permission gating,
multiple sets, metadata, new years, local dates, invalid inputs, server-error
retries, and repeat-submission prevention. Screenshots check assets and mobile
overflow.

To include the unmocked browser-to-API test against a running Compose stack:

```bash
E2E_BASE_URL=http://127.0.0.1:3000 npm run test:e2e
```

CI runs both sets of tests against the built containers. Failure screenshots
and traces are retained in the browser-test-results artifact. Local reports are
available with `npx playwright show-report`.

Authenticated browser tests require separate disposable state and
`E2E_WRITE_TESTS=1`; run with `--grep authenticated`. CI provisions a fixture-only
password automatically. Never run write tests against personal workout state.

The authenticated insertion regression also verifies an unmocked POST through
the proxy, persisted detail after reload, literal note rendering, and exact
analytics totals, then deletes its own inserted workout:

```bash
E2E_BASE_URL=http://127.0.0.1:3000 E2E_WRITE_TESTS=1 npm run test:e2e -- --grep authenticated
```

## Production

The production Dockerfile builds the application with Node and copies only
`dist/` into an unprivileged nginx image. nginx serves the single-page app,
proxies `/api` to the Compose backend, compresses responses, applies immutable
asset caching, and sends restrictive browser security headers.

Run both services from the repository root:

```bash
docker compose up --build
```

Open `http://localhost:3000`.