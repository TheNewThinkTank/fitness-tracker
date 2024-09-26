"""
Date: 2024-02-10
Author: Gustav Collin Rasmussen
Purpose: Definition of popular 1-repetition-maximum formulas
"""

import numpy as np  # type: ignore
from one_rep_max import (  # type: ignore
    OneRepMaxStrategy,
    EpleyStrategy,
    BrzyckiStrategy
    )


def validate_inputs(weight, reps):
    if not isinstance(weight, (int, float, range)):
        raise TypeError("Invalid type for 'weight'. Expected int, float, or range.")
    if not isinstance(reps, (int, float, range)):
        raise TypeError("Invalid type for 'reps'. Expected int, float, or range.")
    return list(weight) if isinstance(weight, range) else [weight], \
           list(reps) if isinstance(reps, range) else [reps]


class OneRepMaxCalculator:
    def __init__(self, strategy):
        self.strategy = strategy

    def calculate(self, weight, reps):
        weights, repetitions = validate_inputs(weight, reps)
        results = []
        for w in weights:
            for r in repetitions:
                if r > 1:  # Ensure valid reps
                    results.append(self.strategy.calculate(w, r))
        return results


class EpleyInvertedStrategy(OneRepMaxStrategy):
    def calculate(self, one_rm, reps, progression):
        return np.log10(progression) * one_rm / (1 + reps / 30)


class BrzyckiInvertedStrategy(OneRepMaxStrategy):
    def calculate(self, one_rm, reps, progression):
        return np.log10(progression) * one_rm * (37 - reps) / 36


class InvertedCalculator:
    def __init__(self, strategy):
        self.strategy = strategy

    def calculate(self, one_rm, reps, progression):
        one_rm_values, reps_values = validate_inputs(one_rm, reps)
        progression_values = [progression] if isinstance(progression, (int, float)) else list(progression)

        results = []
        for one_rm_val in one_rm_values:
            for r in reps_values:
                if r > 1:  # Ensure valid reps
                    for prog in progression_values:
                        results.append(self.strategy.calculate(one_rm_val, r, prog))
        return results


if __name__ == "__main__":
    # Example usage
    epley_calculator = OneRepMaxCalculator(EpleyStrategy())
    brzycki_calculator = OneRepMaxCalculator(BrzyckiStrategy())

    epley_results = epley_calculator.calculate(100, 10)
    brzycki_results = brzycki_calculator.calculate(100, 10)
