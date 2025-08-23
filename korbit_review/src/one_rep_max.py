"""acsm_1rm, epley or brzycki formulas
are used to implement the 1RM estimation.

ACSM 1RM formula

.. math::
    \\frac{w}{\\frac{100 - r \\cdot 2.5}{100}}

Epley 1RM formula

.. math::
    w \\cdot \\frac{1 + r}{30}

Brzycki 1RM formula

.. math::
    w \\cdot \\frac{36}{37 - r}

"""

from abc import ABC, abstractmethod
import numpy as np


class OneRepMaxStrategy(ABC):
    """Abstract class for one-repetition-maximum estimation strategies.
    """
    @abstractmethod
    def estimate(self, weight, reps):
        pass


class EpleyStrategy(OneRepMaxStrategy):
    """Epley formula for one-repetition-maximum estimation.
    """
    def estimate(self, weight, reps):
        return weight * (1 + reps / 30)


class BrzyckiStrategy(OneRepMaxStrategy):
    """Brzycki formula for one-repetition-maximum estimation.
    """
    def estimate(self, weight, reps):
        return weight * 36 / (37 - reps)


class ACSMStrategy(OneRepMaxStrategy):
    """ACSM formula for one-repetition-maximum estimation.
    """
    def estimate(self, weight, reps):
        denominator = (100 - reps * 2.5) / 100
        # Check if denominator has any zeros
        if np.any(denominator == 0):
            raise ValueError(
                "denominator is zero in ACSM formula for one or more entries."
                )
        return weight / denominator
