FROM python:3.15.0-slim@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58 AS requirements

ARG UV_VERSION=0.13.6

WORKDIR /build

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

COPY pyproject.toml uv.lock ./
RUN uv export \
    --locked \
    --no-default-groups \
    --no-emit-project \
    --format requirements.txt \
    --output-file requirements.txt

FROM python:3.15.0-alpine@sha256:2699b90f4d562a22e2dd076c82f964032f64814204bff36d271a54ba4cc2c7e2 AS runtime

LABEL org.opencontainers.image.title="Fitness Tracker API" \
    org.opencontainers.image.version="0.1.0" \
    org.opencontainers.image.source="https://github.com/TheNewThinkTank/fitness-tracker" \
    org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FITNESS_TRACKER_DATA_DIR=/data \
    FITNESS_TRACKER_STATE_DIR=/state

RUN addgroup --gid 10001 --system app && \
    adduser --uid 10001 --system --disabled-password --ingroup app app && \
    mkdir -p /state && chown app:app /state && chmod 700 /state

WORKDIR /app

COPY --from=requirements /build/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r requirements.txt && \
    rm requirements.txt

COPY --chown=app:app src ./src
COPY --chown=app:app .config/settings.toml ./.config/settings.toml
COPY --chown=app:app docs/project_docs/exercises/muscles_and_exercises.yaml ./docs/project_docs/exercises/
COPY --chown=app:app docs/project_docs/Workout-Programs/workout_programs.yml docs/project_docs/Workout-Programs/workout-program-detail.yml ./docs/project_docs/Workout-Programs/

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=3)"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-server-header"]
