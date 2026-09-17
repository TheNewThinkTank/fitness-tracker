# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Permanent stored workout UUIDs, including an idempotent migration that
    preserves existing API URLs. All 253 bundled workouts have been backfilled;
    see the [migration guide](../examples/EXAMPLES.md#migrate-existing-workout-ids)
    for external data directories.
- Desktop and mobile Playwright coverage for year selection, pagination,
    duplicate-day workout details, and error recovery. Container CI is configured
    to run these workflows and retain failure screenshots and traces.

### Changed

- Imports, API records, and standalone validation share Pydantic calendar-date
    and record-structure validation while preserving additional metadata.
- Workout reads use cached, validated snapshots and a UUID index. File changes,
    replacement, deletion, and moves between years invalidate the relevant
    entries without a server restart or repeated parsing of unchanged YAML.

### Fixed

- Historical and mixed-year imports now select the database for each requested
    workout date instead of writing everything into the current year's file.
    Archive contents must match the requested date.
- Invalid calendar dates are rejected at import. Malformed legacy records are
    logged and omitted instead of breaking valid API results.
- Deleting and reopening a database no longer allows a new workout to reuse a
    deleted workout's public ID. Stored IDs survive updates and document
    renumbering.
- Non-ASCII API tokens return `401` instead of raising a server error.

### Verification status

Local verification on 2026-09-14: 134 backend tests passed with 2 skipped,
5 frontend unit tests passed, and all 8 desktop/mobile browser tests passed
against FastAPI with Vite's token-protected proxy. Ruff, mypy, Svelte/TypeScript
checks, and the production frontend build also passed.

Container runtime verification remains outstanding because the Docker Desktop
and OrbStack daemons were unavailable. The configured container CI workflow is
not a claim that these changes have already passed against the production
containers locally.

### Planned

The existing roadmap items below are separate from the completed changes above.

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

## [0.1.0] - 2026-09-02

### Added

- Responsive Svelte 5 and TypeScript workout browser with year selection,
    global ordering, pagination, loading and error states, and detailed set views
- Paginated `/workouts` API, stable workout IDs, available-year discovery, and
    runtime response validation in the browser
- FastAPI integration tests, frontend tests, pull-request CI, npm and Docker
    dependency updates, and generated JSON/YAML OpenAPI contracts
- Optional API token protection injected by the same-origin nginx proxy

### Changed

- Replaced the legacy Rollup/Sirv frontend with Vite and an unprivileged nginx
    production image
- Centralized environment settings under the `FITNESS_TRACKER_` prefix and made
    missing-year reads non-mutating
- Split Python API, analytics, integration, documentation, and development
    dependencies and committed the Poetry lockfile
- Hardened containers with read-only filesystems, non-root users, dropped Linux
    capabilities, health-gated startup, loopback port binding, and log rotation

### Fixed

- Preserved multiple workouts logged on the same date
- Restored Python 3.11 compatibility and aligned FastAPI with patched Starlette
- Added atomic YAML writes, synchronized database lifecycle, import schema
    validation, and confined archive-file lookup
- Removed duplicate frontend mounting, hard-coded API URLs, silent network
    failures, stale default-year behavior, and mobile layout overflow

<!--
### Changed
### Removed
### Fixed

## [0.0.2] - YYYY-MM-DD

### Added

- src/utils/google_sheets module for interacting with google sheets

### Changed

- src/utils/get_bodyweight.py: uses new google_sheets module

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
