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

Copy the environment template and fill in your values:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| `USER` | Your OS username |
| `EMAIL` | Your Google account email (used for Drive access) |
| `ATHLETE` | Athlete folder name in your Google Drive data path |
| `GOOGLE_DRIVE_DATA_PATH` | Path to workout data root. Use `data` for local dev |

### Docker Compose

```bash
docker compose up
```

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

### Docker (single container)

Build and run locally, or pull the published image:

```bash
# Build locally
docker build -t fitness-tracker:latest .

# Or pull the published image
# docker pull ghcr.io/thenewthinktank/fitness-tracker:latest

docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/local_assets/credentials.json:/code/local_assets/credentials.json:ro" \
  fitness-tracker:latest
```

The `--env-file .env` flag supplies all required environment variables.
The credentials volume mount is read-only, matching the container runtime behaviour.

---

## Container image

The image is published to GitHub Container Registry on every push to `main`:

```
ghcr.io/thenewthinktank/fitness-tracker:latest
```

The repository is public so no pull credentials are required.

The image exposes two health endpoints intended for use by container orchestrators:

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Liveness — is the process running? |
| `GET /readyz` | Readiness — is the database reachable? |

Kubernetes deployment manifests and GitOps configuration live in the
[homelab](https://github.com/TheNewThinkTank/homelab) repository.

---

## For contributors

[Project tracking](https://thenewthinktank.atlassian.net/jira/software/projects/FT/boards/2)
