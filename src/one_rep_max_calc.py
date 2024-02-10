"""
Date: 2024-02-10
Author: Gustav Collin Rasmussen
Purpose: Definition of popular 1-repetition-maximum formulas
"""

import numpy as np


def epley(weight, reps):
    results = []

    if isinstance(weight, (int, float)):
        w_values = [weight]  # Convert to list for consistency
    elif isinstance(weight, range):
        w_values = list(weight)
    else:
        raise TypeError("Invalid type for 'weight'. Expected int, float, or range.")

    if isinstance(reps, (int, float)):
        reps_values = [reps]  # Convert to list for consistency
    elif isinstance(reps, range):
        reps_values = list(reps)
    else:
        raise TypeError("Invalid type for 'reps'. Expected int, float, or range.")

    for w_val in w_values:
        for r in reps_values:
            assert r > 1
            results.append(w_val * (1 + r / 30))
    return results


def brzycki(weight, reps):
    results = []

    if isinstance(weight, (int, float)):
        w_values = [weight]  # Convert to list for consistency
    elif isinstance(weight, range):
        w_values = list(weight)
    else:
        raise TypeError("Invalid type for 'weight'. Expected int, float, or range.")

    if isinstance(reps, (int, float)):
        reps_values = [reps]  # Convert to list for consistency
    elif isinstance(reps, range):
        reps_values = list(reps)
    else:
        raise TypeError("Invalid type for 'reps'. Expected int, float, or range.")

    for w_val in w_values:
        for r in reps_values:
            assert r > 1
            results.append(w_val * 36 / (37 - r))
    return results


def epley_inverted(one_rm, reps, progression):
    results = []

    if isinstance(one_rm, (int, float)):
        one_rm_values = [one_rm]  # Convert to list for consistency
    elif isinstance(one_rm, range):
        one_rm_values = list(one_rm)
    else:
        raise TypeError("Invalid type for 'one_rm'. Expected int, float, or range.")

    if isinstance(reps, (int, float)):
        reps_values = [reps]  # Convert to list for consistency
    elif isinstance(reps, range):
        reps_values = list(reps)
    else:
        raise TypeError("Invalid type for 'reps'. Expected int, float, or range.")

    if isinstance(progression, (int, float)):
        progression_values = [progression]  # Convert to list for consistency
    elif isinstance(progression, range):
        progression_values = list(progression)
    else:
        raise TypeError("Invalid type for 'progression'. Expected int, float, or range.")

    for one_rm_val in one_rm_values:
        for r in reps_values:
            assert r > 1
            for prog in progression_values:
                results.append(np.log10(prog) * one_rm_val / (1 + r / 30))
    return results


def brzycki_inverted(one_rm, reps, progression):
    results = []

    if isinstance(one_rm, (int, float)):
        one_rm_values = [one_rm]  # Convert to list for consistency
    elif isinstance(one_rm, range):
        one_rm_values = list(one_rm)
    else:
        raise TypeError("Invalid type for 'one_rm'. Expected int, float, or range.")

    if isinstance(reps, (int, float)):
        reps_values = [reps]  # Convert to list for consistency
    elif isinstance(reps, range):
        reps_values = list(reps)
    else:
        raise TypeError("Invalid type for 'reps'. Expected int, float, or range.")

    if isinstance(progression, (int, float)):
        progression_values = [progression]  # Convert to list for consistency
    elif isinstance(progression, range):
        progression_values = list(progression)
    else:
        raise TypeError("Invalid type for 'progression'. Expected int, float, or range.")

    for one_rm_val in one_rm_values:
        for r in reps_values:
            assert r > 1
            for prog in progression_values:
                results.append(np.log10(prog) * one_rm_val * (37 - r) / 36)
    return results
