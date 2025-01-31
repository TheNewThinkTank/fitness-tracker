FROM python:3.11-slim AS requirements-stage

WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11

WORKDIR /code

ARG USER
ARG ATHLETE
ARG EMAIL
ARG ALTERNATIVE_EMAIL

ENV USER=${USER}
ENV ATHLETE=${ATHLETE}
ENV EMAIL=${EMAIL}
ENV ALTERNATIVE_EMAIL=${ALTERNATIVE_EMAIL}

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
# ENV PATH /home/${USERNAME}/.local/bin:${PATH}
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# COPY .env .env
COPY ./src /code/src
COPY ./data /code/data
# COPY .config/config.yml /code/.config/config.yml
COPY .config/settings.toml /code/.config/settings.toml
# COPY ./app /code/app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["python", "src/main.py"]
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
