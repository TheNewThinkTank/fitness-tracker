import json
import subprocess
from pathlib import Path

import pytest
import yaml


def workflow(filename):
    workflow_file = Path(__file__).parents[1] / ".github" / "workflows" / filename
    return yaml.safe_load(workflow_file.read_text())


@pytest.fixture
def release_script(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for variable, value in {
        "GITHUB_SHA": "a" * 40,
        "GITHUB_OWNER": "thenewthinktank",
        "IMAGE_NAME": "fitness-tracker",
        "IMAGE_TAG": "main-102.3",
    }.items():
        monkeypatch.setenv(variable, value)
    steps = workflow("job_docker_image.yml")["jobs"]["build_scan_and_push"]["steps"]
    command = next(
        step["run"]
        for step in steps
        if step["name"] == "Record immutable release references"
    ).splitlines()
    assert command[0] == "python3 - <<'PY'"
    assert command[-1] == "PY"
    return compile("\n".join(command[1:-1]), "record-image-release", "exec")


def test_release_artifact_pins_matching_component_tags(release_script, monkeypatch):
    inspected = []

    def inspect_image(command, *, text):
        assert command[:3] == ["docker", "image", "inspect"]
        assert text is True
        reference = command[3]
        inspected.append(reference)
        repository = reference.split(":", 1)[0]
        digest = "b" * 64 if repository.endswith("-frontend") else "a" * 64
        return json.dumps(
            [
                {
                    "RepoDigests": [
                        f"{repository}@sha256:{digest}",
                        f"ghcr.io/another/image@sha256:{'c' * 64}",
                    ]
                }
            ]
        )

    monkeypatch.setattr(subprocess, "check_output", inspect_image)
    exec(release_script, {})
    release = json.loads(Path("image-release.json").read_text())
    backend = "ghcr.io/thenewthinktank/fitness-tracker:main-102.3"
    frontend = "ghcr.io/thenewthinktank/fitness-tracker-frontend:main-102.3"
    assert inspected == [backend, frontend]
    assert release == {
        "revision": "a" * 40,
        "tag": "main-102.3",
        "backend": f"{backend}@sha256:{'a' * 64}",
        "frontend": f"{frontend}@sha256:{'b' * 64}",
    }


@pytest.mark.parametrize("component", ["backend", "frontend"])
@pytest.mark.parametrize("digest_count", [0, 2])
def test_release_artifact_rejects_missing_or_ambiguous_digests(
    release_script, monkeypatch, component, digest_count
):
    def inspect_image(command, *, text):
        assert text is True
        repository = command[3].split(":", 1)[0]
        observed_component = (
            "frontend" if repository.endswith("-frontend") else "backend"
        )
        count = digest_count if observed_component == component else 1
        return json.dumps(
            [{"RepoDigests": [f"{repository}@sha256:{'a' * 64}"] * count}]
        )

    monkeypatch.setattr(subprocess, "check_output", inspect_image)
    with pytest.raises(SystemExit, match=f"published digest for {component}"):
        exec(release_script, {})
    assert not Path("image-release.json").exists()


def test_publication_requires_main_tests_and_both_image_scans():
    jobs = workflow("wf.yml")["jobs"]
    publisher = jobs["docker_image_workflow"]
    assert publisher["if"] == (
        "github.event_name != 'pull_request' && github.ref == 'refs/heads/main'"
    )
    assert publisher["needs"] == "containers"
    assert jobs["containers"]["needs"] == ["qualify_code", "frontend"]
    assert publisher["with"]["image-tag"] == (
        "main-${{ github.run_number }}.${{ github.run_attempt }}"
    )
    release_job = workflow("job_docker_image.yml")["jobs"]["build_scan_and_push"]
    assert release_job["permissions"] == {"contents": "read", "packages": "write"}
    steps = release_job["steps"]
    names = [step["name"] for step in steps]
    for scan_name in (
        "Scan backend image for vulnerabilities",
        "Scan frontend image for vulnerabilities",
    ):
        scan = steps[names.index(scan_name)]
        assert scan["with"]["fail-build"] is True
        assert scan["with"]["severity-cutoff"] == "high"
        assert scan["with"]["only-fixed"] is False
        assert names.index(scan_name) < names.index("Push to GitHub Packages")
    assert (
        names.index("Push to GitHub Packages")
        < names.index("Record immutable release references")
        < names.index("Upload immutable release references")
    )
    artifact = steps[names.index("Upload immutable release references")]
    assert artifact["with"]["name"] == "fitness-tracker-images-${{ inputs.image-tag }}"
    assert artifact["with"]["if-no-files-found"] == "error"
