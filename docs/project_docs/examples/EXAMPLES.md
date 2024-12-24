# Examples

## Getting started

First, clone the project:<br>
`git clone https://github.com/TheNewThinkTank/fitness-tracker.git`

### Upload your workouts

- Add your workout log to the `data` folder under the correct workout date
- Run `./bin/fitcli.sh`, optionally specify the `WORKOUT_DATE` and `TRAINING_PROGRAM` values
- The `bin/fitcli.sh` script will then insert your log(s) into the TinyDB database

### Analyze your data

Run FastAPI web app with Docker from CLI:
`docker-compose up`<br>
then visit this [URL](http://localhost:8080/docs)

Alternatively,

```BASH
docker build -t ftimage .
docker run -d -p 8000:8000 --name ftcontainer ftimage
```

```BASH
python3 src/utils/get_breath_holding.py

./fitcli.sh
./fitcli.sh -d 2024-03-03 -f json
```

### Update Sphinx docs

If you modify the project source code, you might like to update the technical docs (using Sphinx).
This can be done locally as follows:

```BASH
cd docs
make clean
sphinx-apidoc -o ./source ../src
make html
```

### Scan Docker Image locally

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
