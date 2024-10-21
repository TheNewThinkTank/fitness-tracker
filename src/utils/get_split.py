
from enum import Enum, unique


@unique
class Split(Enum):
    CHEST = 1
    BACK = 2
    LEGS = 3
