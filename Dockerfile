FROM python:3.12 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

# TODO: create empty requirements.txt here?
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
# ENV PATH /home/${USERNAME}/.local/bin:${PATH}
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# TODO: switch below to .env and using helper.config_loader
COPY local_assets/private_config.json /code/local_assets/private_config.json

COPY ./src /code/src
COPY ./data /code/data
COPY .config/config.yml /code/.config/config.yml

# COPY ./app /code/app

CMD ["python", "src/main.py"]
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
