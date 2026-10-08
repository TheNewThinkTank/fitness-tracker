"""Shared, offline metric rules for recorded training data."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import math
import re
from typing import Literal, Mapping

Formula = Literal["epley", "brzycki", "acsm"]
LoadKind = Literal["external", "bodyweight", "assisted", "unknown"]
MAX_ESTIMATION_REPS = 10
EXERCISE_ALIASES = {
    "bb_bench_press": "bench_press",
    "barbell_bench_press": "bench_press",
    "bb_squat": "squat",
    "bb_deadlift": "deadlift",
    "bb_front_squat": "front_squat",
    "bb_sumo_deadlift": "sumo_deadlift",
    "legpress": "leg_press",
    "leg_extention": "leg_extension",
    "rdl": "romanian_deadlift",
    "romanian_deadlift_(rdl)": "romanian_deadlift",
}
NAMED_LOADS = {"Sidea_9012_Olympic_Hex_Bar": 31.0}


def canonical_exercise(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "_")
    return EXERCISE_ALIASES.get(normalized, normalized)


def positive_number(value: object, *, allow_zero: bool = False) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number < 0 or (number == 0 and not allow_zero):
        return None
    return number


@dataclass(frozen=True)
class ParsedLoad:
    kind: LoadKind
    total_kg: float | None
    external_kg: float | None
    assistance_kg: float | None = None
    reason: str | None = None


def parse_load(
    expression: str,
    bodyweight_kg: float | None = None,
    named_loads: Mapping[str, float] | None = None,
) -> ParsedLoad:
    raw = re.sub(r"\s*kg\s*$", "", expression.strip(), flags=re.IGNORECASE)
    for name, weight in (named_loads or NAMED_LOADS).items():
        raw = raw.replace(name, str(weight))
    body_match = re.fullmatch(
        r"BODYWEIGHT(?:\s*([+-])\s*(\d+(?:\.\d+)?|POWERBAND_[A-Z]+))?",
        raw,
        flags=re.IGNORECASE,
    )
    if body_match:
        sign, modifier = body_match.groups()
        kind: LoadKind = "assisted" if sign == "-" else "bodyweight"
        if modifier and modifier.upper().startswith("POWERBAND_"):
            return ParsedLoad(kind, None, None, reason="unknown_band_resistance")
        offset = float(modifier or 0)
        mass = positive_number(bodyweight_kg)
        total = None if mass is None else mass + (-offset if sign == "-" else offset)
        if total is not None and total < 0:
            return ParsedLoad(kind, None, None, reason="assistance_exceeds_bodyweight")
        return ParsedLoad(
            kind,
            total,
            offset if sign == "+" else 0.0,
            offset if sign == "-" else None,
            "missing_bodyweight" if mass is None else None,
        )
    arithmetic = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([+-])\s*(\d+(?:\.\d+)?)", raw)
    if arithmetic:
        first, operator, second = arithmetic.groups()
        value = float(first) + (float(second) if operator == "+" else -float(second))
    elif re.fullmatch(r"\d+(?:\.\d+)?", raw):
        value = float(raw)
    else:
        return ParsedLoad("unknown", None, None, reason="unsupported_load")
    validated_value = positive_number(value, allow_zero=True)
    if validated_value is None:
        return ParsedLoad("unknown", None, None, reason="invalid_load")
    return ParsedLoad("external", validated_value, validated_value)


def estimate_one_rm(weight_kg: float, reps: int, formula: Formula = "epley") -> float | None:
    weight = positive_number(weight_kg)
    if weight is None or isinstance(reps, bool) or not 1 <= reps <= MAX_ESTIMATION_REPS:
        return None
    if reps == 1:
        return weight
    if formula == "epley":
        return weight * (1 + reps / 30)
    if formula == "brzycki":
        return weight * 36 / (37 - reps)
    if formula == "acsm":
        return weight / (1 - reps * 0.025)
    raise ValueError("Unsupported 1RM formula")


def session_duration(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    try:
        start_clock = time.fromisoformat(start)
        end_clock = time.fromisoformat(end)
        beginning = datetime.combine(date(2000, 1, 1), start_clock)
        ending = datetime.combine(date(2000, 1, 1), end_clock)
        if ending < beginning:
            ending += timedelta(days=1)
        minutes = (ending - beginning).total_seconds() / 60
    except (ValueError, TypeError):
        return None
    return minutes if 0 < minutes <= 720 else None


def duration_seconds(value: str | None) -> float | None:
    if not value:
        return None
    clock = re.fullmatch(r"(?:(\d+):)?(\d{1,2}):(\d{2}(?:\.\d+)?)", value.strip())
    if clock:
        hours, minutes, seconds = clock.groups()
        if int(minutes) >= 60 or float(seconds) >= 60:
            return None
        return positive_number(int(hours or 0) * 3600 + int(minutes) * 60 + float(seconds))
    amount = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(s|sec|seconds?|m|min|minutes?)?", value.strip(), re.IGNORECASE)
    if amount:
        number, unit = amount.groups()
        return positive_number(float(number) * (60 if unit and unit.lower().startswith("m") else 1))
    return None


def height_cm(value: object) -> float | None:
    if isinstance(value, (float, int)):
        return positive_number(value)
    if isinstance(value, str):
        match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(cm|m)?", value.strip(), re.IGNORECASE)
        if match:
            amount, unit = match.groups()
            return positive_number(float(amount) * (100 if unit and unit.lower() == "m" else 1))
    return None