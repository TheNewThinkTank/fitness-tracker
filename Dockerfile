FROM python:3.13-slim AS requirements-stage

WORKDIR /tmp
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
  pip install poetry && poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.13-slim

RUN useradd --uid 1000 --create-home --shell /bin/bash appuser

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
  pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
  apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY ./src /code/src
COPY ./data /code/data
COPY .config/settings.toml /code/.config/settings.toml

RUN chown -R appuser:appuser /code

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
