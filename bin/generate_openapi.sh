#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN=$(command -v python3)
fi
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" - "$@" <<'PY'
import argparse
import json
from pathlib import Path

import yaml

from src.main import app
from src.common.workout_types import WorkoutData
from src.utils.config import PROJECT_ROOT

parser = argparse.ArgumentParser(description="Generate or verify API and workout editor schemas.")
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
output_directory = PROJECT_ROOT / "docs/project_docs/dev-docs/API-Schema"
schema = app.openapi()
workout_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", **WorkoutData.model_json_schema()}
artifacts = {
    output_directory / "openapi.json": (schema, json.dumps(schema, indent=2) + "\n"),
    output_directory / "openapi.yaml": (schema, yaml.safe_dump(schema, sort_keys=False)),
    PROJECT_ROOT / ".config/yaml_schema.json": (workout_schema, json.dumps(workout_schema, indent=2) + "\n"),
}
for path, (expected, text) in artifacts.items():
    if args.check:
        actual = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None
        if actual != expected:
            raise SystemExit(f"Schema drift: {path.relative_to(PROJECT_ROOT)}; run bin/generate_openapi.sh")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
print("API and workout editor schemas verified." if args.check else "API and workout editor schemas generated.")
PY
