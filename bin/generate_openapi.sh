#!/usr/bin/env bash

set -e

# Add the src directory to the Python path
# export PYTHONPATH=$(pwd)/src

# Start the FastAPI application
poetry run uvicorn src.main:app --host 127.0.0.1 --port 8000 &
# uvicorn src.main:app --host 0.0.0.0 --port 80
PID=$!
sleep 5  # Give the server time to start

# Ensure the directory exists
mkdir -p docs/schema

# Fetch the OpenAPI JSON and format it
curl http://127.0.0.1:8000/openapi.json | jq . > docs/project_docs/API-Schema/openapi.json

# Kill the server
kill $PID
