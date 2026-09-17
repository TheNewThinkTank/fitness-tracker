# Scan Docker Image locally

Assuming you have a `.env` file at the root of your repo (see `.env.example`):

```text
FITNESS_TRACKER_DATA_DIR=data
FITNESS_TRACKER_ATHLETE=default
```

Build the image (env vars are injected at runtime, not build time):

```bash
docker build -t fitness-tracker:latest .
```

Then scan with Grype:

```bash
grype fitness-tracker:latest
```

Scanning also runs automatically in CI via `job_docker_image.yml` using
[Anchore scan-action](https://github.com/anchore/scan-action).
Builds fail on HIGH or CRITICAL severity findings.
