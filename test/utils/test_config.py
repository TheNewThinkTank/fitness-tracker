"""Configuration isolation without reading the operator's private environment."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("disabled", [False, True])
def test_dotenv_disable_switch_preserves_default_local_loading(
    tmp_path: Path, disabled: bool
) -> None:
    root = Path(__file__).resolve().parents[2]
    project = tmp_path / "project"
    configuration = project / "src/utils/config.py"
    configuration.parent.mkdir(parents=True)
    (project / ".config").mkdir()
    configuration.write_text((root / "src/utils/config.py").read_text())
    (project / ".config/settings.toml").write_text((root / ".config/settings.toml").read_text())
    (project / ".env").write_text("FITNESS_TRACKER_API_TOKEN=fixture-value\n")
    environment = {
        key: value for key, value in os.environ.items()
        if not key.startswith("FITNESS_TRACKER_") and key != "PYTHON_DOTENV_DISABLED"
    }
    if disabled:
        environment["PYTHON_DOTENV_DISABLED"] = "1"
    expected = "" if disabled else "fixture-value"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import runpy; settings=runpy.run_path({str(configuration)!r})['settings']; "
            f"assert settings.API_TOKEN == {expected!r}; "
            "print('Configuration isolation verified.')",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
        cwd=project,
    )
    assert result.stdout.strip() == "Configuration isolation verified."
