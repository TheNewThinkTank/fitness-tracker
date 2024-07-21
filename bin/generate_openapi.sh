#!/usr/bin/env bash

set -e

# Add the src directory to the Python path
# export PYTHONPATH=$(pwd)/src

find_available_port() {
  local port=8000
  while lsof -i:$port &>/dev/null; do
    port=$((port+1))
  done
  echo $port
}

PORT=$(find_available_port)

# Start the FastAPI application
poetry run uvicorn src.main:app --host 127.0.0.1 --port $PORT &
PID=$!
sleep 10  # Give the server time to start

# Ensure the directory exists
mkdir -p docs/project_docs/API-Schema/

# Fetch the OpenAPI JSON and format it
curl http://127.0.0.1:$PORT/openapi.json | jq . > docs/project_docs/API-Schema/openapi.json

curl -v http://127.0.0.1:$PORT/openapi.yaml -o docs/project_docs/API-Schema/openapi.yaml

# Kill the server
kill $PID
