"""
Athlete profiling
"""

from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class Athlete:
    """."""

    name: str
    dob: str  # date of birth
    # country/nationality
    # weight_training_logs
    # cardio_logs
    gender: str
    height: int  # [cm]
    bodyweight: int  # [kg]
    hr_rest: Optional[int] = (0,)
    sport: Optional[str] = ("",)
    death_date: Optional[str] = ("",)

    def get_bmi(self) -> float:
        """
        Body mass index is a value derived from the mass and height of a person.
        The BMI is defined as the body mass divided by the square of the body height,
        and is expressed in units of kg/m²,
        resulting from mass in kilograms and height in metres
        """
        bmi = self.bodyweight / self.height**2
        return float(f"{bmi:.5f}")

    def get_age(self):
        """TODO: check if this works for leap years and edge cases."""

        dob = datetime.datetime.strptime(self.dob, "%Y-%m-%d").date()

        if not self.death_date:
            today = datetime.date.today()
            return int((today - dob).days / 365.2425)
        else:
            dod = datetime.datetime.strptime(self.death_date, "%Y-%m-%d").date()
            return int((dod - dob).days / 365.2425)

    def _get_gender_pronoun(self):
        return {"M": "He", "F": "She"}.get(self.gender, "They")

    def __str__(self) -> str:
        if self.death_date:
            msg = (
                f"The athlete {self.name} lived to be {self.get_age()} years old."
                f" {self._get_gender_pronoun()} had a BMI of {self.get_bmi()} kg/m²"
            )
            return msg
        msg = (
            f"The athlete {self.name} is {self.get_age()} years old."
            f" {self._get_gender_pronoun()} has a BMI of {self.get_bmi()} kg/m²"
        )
        return msg

    def _get_hr_max(self):
        # hr_max = 220 - self.get_age()  # in beats per minute (bpm)
        hr_max = 205.8 - 0.685 * self.get_age()
        return hr_max

    def get_vo2_max(self):
        """The units for VO2 max are:
        milliliters of oxygen per kilogram of body weight per minute (mL/kg/min)
        """
        if not self.hr_rest:
            return "Resting heart rate is unknown"
        # The heart rate ratio method:
        vo2_max = 15.3 * self._get_hr_max() / self.hr_rest
        return float(f"{vo2_max:.5f}")


@dataclass
class Team:
    """."""

    name: str
    members: list
    # country/nationality,
    sport: Optional[str]
