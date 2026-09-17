# Fitness Tracker frontend

The frontend is a Svelte 5 and TypeScript application built with Vite. It loads
available years, paginated workout summaries, and exercise details from relative
`/api` routes.

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
construction, error handling, runtime response validation, and server rendering.

### Browser workflows

Install Chromium once, then run Playwright on desktop and mobile viewports:

```bash
npx playwright install chromium
npm run test:e2e
```

Playwright builds the frontend and starts an isolated preview on port 4173.
Set `E2E_PORT` to use another port. Deterministic API fixtures cover year
selection, pagination, global ordering, duplicate-day details, and error/retry
behavior. Screenshots also check that the brand image loads and the page does
not overflow on mobile.

To include the unmocked browser-to-API test against a running Compose stack:

```bash
E2E_BASE_URL=http://127.0.0.1:3000 npm run test:e2e
```

CI runs both sets of tests against the built containers. Failure screenshots
and traces are retained in the browser-test-results artifact. Local reports are
available with `npx playwright show-report`.

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