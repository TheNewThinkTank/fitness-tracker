"""Historical body measurements; no current-value substitution or remote reads."""

from datetime import date as CalendarDate
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.common.workout_types import parse_workout_date


class BodyMeasurement(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    date: CalendarDate
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    waist_cm: float | None = Field(default=None, gt=0, le=400)
    resting_heart_rate: int | None = Field(default=None, ge=20, le=250)

    @field_validator("date", mode="before")
    @classmethod
    def measured_date(cls, value: Any) -> CalendarDate:
        result = parse_workout_date(value)
        if not 1900 <= result.year <= 2100:
            raise ValueError("Measurement date must be between 1900 and 2100")
        return result

    @model_validator(mode="after")
    def has_measurement(self) -> "BodyMeasurement":
        if self.weight_kg is None and self.waist_cm is None and self.resting_heart_rate is None:
            raise ValueError("Provide at least one measurement")
        return self