"""Validated program targets and exercise metadata, including legacy YAML."""

from datetime import date
from pathlib import Path
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
import yaml

from src.common.metrics import canonical_exercise
from src.utils.config import PROJECT_ROOT, settings
from src.utils.get_program import parse_date
from src.utils.state_store import state_store
import json


class ExerciseTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exercise_id: str
    sets: int = Field(ge=1, le=100)
    reps_min: int | None = Field(default=None, ge=0, le=1000)
    reps_max: int | None = Field(default=None, ge=0, le=1000)
    max_reps: bool = False

    @model_validator(mode="after")
    def rep_range(self) -> "ExerciseTarget":
        if self.max_reps:
            if self.reps_min is not None or self.reps_max is not None:
                raise ValueError("Max-rep targets cannot also have a numeric range")
        elif self.reps_min is None or self.reps_max is None or self.reps_min > self.reps_max:
            raise ValueError("Provide an ordered minimum and maximum rep range")
        self.exercise_id = canonical_exercise(self.exercise_id)
        return self


class ProgramSplit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=100)
    targets: list[ExerciseTarget] = Field(max_length=100)


class TrainingProgram(BaseModel):
    id: str
    name: str
    start: date
    end: date | None
    splits: list[str]
    planned_workouts: int | None
    targets: list[ProgramSplit]


def metadata_path(setting: str) -> Path:
    path = Path(str(settings[setting])).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def _yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        content = yaml.safe_load(handle)
    if not isinstance(content, dict):
        raise ValueError(f"Training metadata must be a mapping: {path.name}")
    return content


def split_id(name: str) -> str:
    normalized = name.split(" (")[0].strip().lower().replace(" ", "_")
    if normalized == "fullbody":
        return "full_body"
    if normalized.startswith("fullbody_"):
        return "full_body_" + normalized.removeprefix("fullbody_")
    return normalized


def parse_target(exercise: str, value: Any) -> ExerciseTarget | None:
    if isinstance(value, dict):
        return ExerciseTarget.model_validate({**value, "exercise_id": canonical_exercise(exercise)})
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"(\d+) sets? of (?:(\d+)(?:-(\d+))?|(max)) reps?", value.strip(), re.IGNORECASE)
    if not match:
        return None
    sets, minimum, maximum, max_reps = match.groups()
    return ExerciseTarget(
        exercise_id=canonical_exercise(exercise),
        sets=int(sets),
        reps_min=int(minimum) if minimum else None,
        reps_max=int(maximum or minimum) if minimum else None,
        max_reps=bool(max_reps),
    )


def load_programs() -> list[TrainingProgram]:
    programs = _yaml(metadata_path("WORKOUT_PROGRAMS")).get("programs", {})
    detail_path = settings.get("PROGRAM_TARGETS", "docs/project_docs/Workout-Programs/workout-program-detail.yml")
    path = Path(str(detail_path))
    details = _yaml(path if path.is_absolute() else PROJECT_ROOT / path)
    result = []
    for identifier, program in programs.items():
        if not isinstance(program, dict):
            continue
        start = parse_date(program.get("start"))
        if start is None:
            continue
        targets = []
        for name, prescriptions in details.get(identifier, {}).items():
            if not isinstance(prescriptions, dict):
                continue
            parsed = [target for exercise, value in prescriptions.items() if (target := parse_target(exercise, value)) is not None]
            if parsed:
                targets.append(ProgramSplit(id=split_id(name), targets=parsed))
        planned = program.get("number_of_workouts")
        parsed_program = TrainingProgram(
            id=identifier,
            name=program["name"],
            start=start,
            end=parse_date(program.get("end")),
            splits=[split_id(name) for name in program.get("splits", [])],
            planned_workouts=planned if isinstance(planned, int) and planned > 0 else None,
            targets=targets,
        )
        override = state_store.configuration(f"program:{identifier}")
        if override:
            values = json.loads(override)
            parsed_program.planned_workouts = values.get("planned_workouts")
            parsed_program.targets = [ProgramSplit.model_validate(section) for section in values.get("targets", [])]
        result.append(parsed_program)
    return sorted(result, key=lambda program: program.start)


def program_for_date(programs: list[TrainingProgram], workout_date: date) -> TrainingProgram | None:
    matching = [program for program in programs if program.start <= workout_date and (program.end is None or workout_date <= program.end)]
    return max(matching, key=lambda program: program.start) if matching else None


def exercise_groups() -> dict[str, list[str]]:
    content = _yaml(metadata_path("TRAINING_CATALOGUE"))
    groups = content.get("exercises", content)
    if isinstance(groups, list):
        groups = {name: entries for group in groups if isinstance(group, dict) for name, entries in group.items()}
    result: dict[str, list[str]] = {}

    def visit(entries: list, group: str) -> None:
        for entry in entries:
            if isinstance(entry, str):
                names = result.setdefault(canonical_exercise(entry), [])
                if group not in names:
                    names.append(group)
            elif isinstance(entry, dict):
                for variants in entry.values():
                    if isinstance(variants, list):
                        visit(variants, group)

    for group, entries in groups.items():
        if isinstance(entries, list):
            visit(entries, group)
    return result