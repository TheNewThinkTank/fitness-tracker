# Scan Docker Image locally

Assuming you have a `.env` file at the root of your repo (see `.env.example`):

```text
USER=<USER>
ATHLETE=<ATHLETE>
EMAIL=<EMAIL>
GOOGLE_DRIVE_DATA_PATH=data
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
