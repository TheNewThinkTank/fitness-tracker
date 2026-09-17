#!/usr/bin/env bash

set -euo pipefail

python - <<'PY'
import json
from pathlib import Path

import yaml

from src.main import app

output_directory = Path("docs/project_docs/dev-docs/API-Schema")
output_directory.mkdir(parents=True, exist_ok=True)
schema = app.openapi()
(output_directory / "openapi.json").write_text(
    json.dumps(schema, indent=2) + "\n",
    encoding="utf-8",
)
(output_directory / "openapi.yaml").write_text(
    yaml.safe_dump(schema, sort_keys=False),
    encoding="utf-8",
)
PY
