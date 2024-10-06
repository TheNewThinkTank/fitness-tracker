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
python3 src/helpers/get_breath_holding.py

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
