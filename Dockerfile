FROM python:3.14.7-slim@sha256:caaf356f40667c496d405780745b9ac25771c189a51dfcc42430d531ea09f8a2 AS requirements

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

FROM python:3.14.6-alpine@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92 AS runtime

LABEL org.opencontainers.image.title="Fitness Tracker API" \
    org.opencontainers.image.version="0.1.0" \
    org.opencontainers.image.source="https://github.com/TheNewThinkTank/fitness-tracker" \
    org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FITNESS_TRACKER_DATA_DIR=/data

RUN addgroup --gid 10001 --system app && \
    adduser --uid 10001 --system --disabled-password --ingroup app app

WORKDIR /app

COPY --from=requirements /build/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt && \
    rm requirements.txt

COPY --chown=app:app src ./src
COPY --chown=app:app .config/settings.toml ./.config/settings.toml

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=3)"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-server-header"]
