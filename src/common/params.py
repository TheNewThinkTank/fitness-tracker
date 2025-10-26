"""Common parameter data classes for various operations.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class PlotParams:
    table: object
    year: str
    month: Optional[str] = None
    img_path: Optional[str] = None  # fallback to settings if None

@dataclass
class InsertParams:
    file_format: str
    datatype: str
    dates: str
    workout_number: int = 1
    table: Optional[object] = None

@dataclass
class SimulationConfig:
    n_people: int = 100
    days: int = 365
    seed: Optional[int] = None
    profile: Optional[str] = None

@dataclass
class OneRepMaxConfig:
    method: str = "epley"
    min_reps: int = 1
    max_reps: int = 12
    smoothing_window: int = 1
