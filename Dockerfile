FROM python:3.11 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

# TODO: create empty requirements.txt here?
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
# ENV PATH /home/${USERNAME}/.local/bin:${PATH}
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

COPY ["/Users/gustavcollinrasmussen/Library/CloudStorage/GoogleDrive-gcr84@hotmail.com/My Drive/DATA/fitness-tracker-data/", "/code/data"]
# COPY ./data /code/data

COPY config/config.yml /code/config.yml
# COPY config.json /code/config.json

# COPY ./app /code/app

CMD ["python", "src/main.py"]
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
