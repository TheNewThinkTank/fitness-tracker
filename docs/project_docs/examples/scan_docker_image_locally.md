# Scan Docker Image locally

assuming you have a `.env` file at the root of your repo,
with content:

```text
USER=<USER>
ATHLETE=<ATHLETE>
EMAIL=<EMAIL>
ALTERNATIVE_EMAIL=<ALTERNATIVE_EMAIL>
```

(remember to add `.env` to your `.gitignore` if you wish to keep the content private)

first build image:

```BASH
docker build \              
    --build-arg USER=$(grep -w USER .env | cut -d '=' -f2) \
    --build-arg ATHLETE=$(grep -w ATHLETE .env | cut -d '=' -f2) \
    --build-arg EMAIL=$(grep -w EMAIL .env | cut -d '=' -f2) \
    --build-arg ALTERNATIVE_EMAIL=$(grep -w ALTERNATIVE_EMAIL .env | cut -d '=' -f2) \
    -t fitness-tracker:latest .
```

then run scanning:
`grype fitness-tracker:latest`
