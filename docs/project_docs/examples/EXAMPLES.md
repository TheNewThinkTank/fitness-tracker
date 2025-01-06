# Examples

## Getting started

First, clone the project:<br>
`git clone https://github.com/TheNewThinkTank/fitness-tracker.git`

### Upload your workouts

- Add your workout log to the `data` folder under the correct workout date
- Run `./bin/fitcli.sh`, optionally specify the `WORKOUT_DATE` and `TRAINING_PROGRAM` values
- The `bin/fitcli.sh` script will then insert your log(s) into the TinyDB database

## Running locally

```BASH
# docker-compose up --build
docker compose --profile ci up --build --attach-dependencies --remove-orphans
# then visit http://localhost:5000
```

Run FastAPI with Docker from CLI:
`docker-compose up`<br>
then visit this [URL](http://localhost:8080/docs)

Alternatively,

```BASH
docker build -t ftimage .
docker run -d -p 8000:8000 --name ftcontainer ftimage
```

Or, running without containers:

```BASH
# Start the Backend
cd src
uvicorn main:app --reload

# Start the Frontend
cd frontend
npm run dev
```

**Debugging**:
from the url, open the browser's developer tools (`F12` or `Cmd+Shift+C`)

## Testing endpoints locally

Overview of endpoints

- [root](http://127.0.0.1:8000/)
- [data](http://127.0.0.1:8000/data)
- [dates](http://127.0.0.1:8000/dates)
- [dates_and_splits](http://127.0.0.1:8000/dates_and_splits)
- [date](http://127.0.0.1:8000/dates/{date})
- [exercise](http://127.0.0.1:8000/{date}/exercises/{exercise})

### Example: insert breath holding data in TinyDB

```BASH
python3 src/utils/get_breath_holding.py

./fitcli.sh
./fitcli.sh -d 2024-03-03 -f json
```
