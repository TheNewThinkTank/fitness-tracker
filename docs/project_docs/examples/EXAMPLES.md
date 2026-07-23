# Examples

## Getting started

First, clone the project:<br>
`git clone https://github.com/TheNewThinkTank/fitness-tracker.git`

### Upload your workouts

- Add your workout log to the `data` folder under the correct workout date
- Run `./bin/fitcli.sh`, optionally specify the `WORKOUT_DATE` and `TRAINING_PROGRAM` values
- The `bin/fitcli.sh` script will then insert your log(s) into the TinyDB database

## Running locally

Copy the environment template and fill in your values:

```bash
cp .env.example .env
```

### With Docker Compose (recommended)

```bash
docker compose up
```

- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

### Single container

```bash
docker build -t fitness-tracker:latest .
docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/local_assets/credentials.json:/code/local_assets/credentials.json:ro" \
  fitness-tracker:latest
```

### Without containers

```bash
# Start the backend
uvicorn src.main:app --reload

# Start the frontend (separate terminal)
cd frontend
npm run dev
```

**Debugging**: from the URL, open the browser's developer tools (`F12` or `Cmd+Shift+C`)

## Testing endpoints locally

Overview of endpoints:

- [root](http://127.0.0.1:8000/)
- [data](http://127.0.0.1:8000/data)
- [dates](http://127.0.0.1:8000/dates)
- [dates_and_splits](http://127.0.0.1:8000/dates_and_splits)
- [date](http://127.0.0.1:8000/dates/{date})
- [exercise](http://127.0.0.1:8000/{date}/exercises/{exercise})
- [healthz](http://127.0.0.1:8000/healthz)
- [readyz](http://127.0.0.1:8000/readyz)

### Example: insert breath holding data in TinyDB

```bash
python3 src/utils/get_breath_holding.py

./bin/fitcli.sh
./bin/fitcli.sh -d 2024-03-03 -f json
```
