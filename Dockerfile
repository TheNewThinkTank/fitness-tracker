FROM python:3.11-slim AS requirements-stage

WORKDIR /tmp
RUN pip install poetry && poetry self add poetry-plugin-export
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

RUN useradd --uid 1000 --create-home --shell /bin/bash appuser

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src
COPY ./data /code/data
COPY .config/settings.toml /code/.config/settings.toml

RUN chown -R appuser:appuser /code

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
