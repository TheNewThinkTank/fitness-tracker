FROM python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS requirements

ARG POETRY_VERSION=2.2.1
ARG POETRY_EXPORT_VERSION=1.9.0

WORKDIR /build

RUN pip install --no-cache-dir \
    "poetry==${POETRY_VERSION}" \
    "poetry-plugin-export==${POETRY_EXPORT_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN poetry export \
    --only main \
    --format requirements.txt \
    --output requirements.txt \
    --without-hashes

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
RUN pip install --no-cache-dir --upgrade -r requirements.txt && \
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
