"""
Definition of popular 1-repetition-maximum formulas.
"""

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from one_rep_max import (  # type: ignore
    OneRepMaxStrategy,
    EpleyStrategy,
    BrzyckiStrategy
    )


# class OneRepMaxCalculator:
#     def __init__(self, strategy):
#         self.strategy = strategy

#     def calculate(self, weight, reps):
#         weight, reps = self.validate_inputs(weight, reps)
#         return self.strategy.estimate(weight, reps)

#     @staticmethod
#     def validate_inputs(weight, reps):
#         """Ensure that inputs are either scalars,
#         or vectorized types (Pandas Series, NumPy arrays)."""
#         weight_is_vectorized = isinstance(weight, (pd.Series, np.ndarray))
#         reps_is_vectorized = isinstance(reps, (pd.Series, np.ndarray))

#         # Check if both are vectorized
#         if weight_is_vectorized and reps_is_vectorized:
#             if weight.shape != reps.shape:
#                 raise ValueError("Weight and reps must have the same shape when vectorized.")
#         elif not (np.isscalar(weight) or np.isscalar(reps)):
#             raise TypeError("Invalid input types. Expected both weight and reps to be either scalars or vectorized.")
        
#         return weight, reps


class OneRepMaxCalculator:
    def __init__(self, strategy):
        self.strategy = strategy

    def calculate(self, weight, reps):
        weight, reps = self.validate_inputs(weight, reps)
        return self.strategy.estimate(weight, reps)

    @staticmethod
    def validate_inputs(weight, reps):
        weight_is_vectorized = isinstance(weight, (pd.Series, np.ndarray))
        reps_is_vectorized = isinstance(reps, (pd.Series, np.ndarray))
        
        if weight_is_vectorized and reps_is_vectorized and weight.shape != reps.shape:
            raise ValueError("Weight and reps must have the same shape when vectorized.")
        
        if isinstance(reps, (int, float)) and reps <= 0:
            raise ValueError("Reps must be positive.")
        if isinstance(reps, (np.ndarray, pd.Series)) and (reps <= 0).any():
            raise ValueError("All reps values must be positive.")

        return weight, reps


class EpleyInvertedStrategy(OneRepMaxStrategy):
    def estimate(self, one_rm, reps, progression):
        return np.log10(progression) * one_rm / (1 + reps / 30)


class BrzyckiInvertedStrategy(OneRepMaxStrategy):
    def estimate(self, one_rm, reps, progression):
        return np.log10(progression) * one_rm * (37 - reps) / 36


class InvertedCalculator:
    def __init__(self, strategy):
        self.strategy = strategy

    def calculate(self, one_rm, reps, progression):
        one_rm, reps, progression = self.validate_inputs(one_rm, reps, progression)
        return self.strategy.estimate(one_rm, reps, progression)

    @staticmethod
    def validate_inputs(one_rm, reps, progression):
        """Ensure that inputs are either scalars or Pandas Series."""
        if isinstance(one_rm, (pd.Series, np.ndarray)) and isinstance(reps, (pd.Series, np.ndarray)):
            if one_rm.shape != reps.shape:
                raise ValueError("One RM and reps must have the same shape when using vectors.")
        elif isinstance(one_rm, (int, float)) and isinstance(reps, (int, float)):
            pass  # Single values are acceptable
        else:
            raise TypeError("Invalid input types. Expected both one_rm and reps to be either scalars or pandas Series.")
        
        if not isinstance(progression, (pd.Series, np.ndarray)):
            progression = np.array(progression)  # Convert scalar to array for consistent operations

        return one_rm, reps, progression


def main() -> None:
    # Example usage
    epley_calculator = OneRepMaxCalculator(EpleyStrategy())
    brzycki_calculator = OneRepMaxCalculator(BrzyckiStrategy())
    epley_results = epley_calculator.calculate(100, 10)
    brzycki_results = brzycki_calculator.calculate(100, 10)
    print(epley_results, brzycki_results)


if __name__ == "__main__":
    main()
