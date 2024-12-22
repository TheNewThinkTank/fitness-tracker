
import pytest
import numpy as np
from src.one_rep_max import (  # type: ignore
    EpleyStrategy,
    BrzyckiStrategy
)
from src.one_rep_max_calc import (  # type: ignore
    OneRepMaxCalculator,
    EpleyInvertedStrategy,
    BrzyckiInvertedStrategy,
    InvertedCalculator
)

# Fixtures for strategies and calculators
@pytest.fixture
def epley_calculator():
    return OneRepMaxCalculator(EpleyStrategy())

@pytest.fixture
def brzycki_calculator():
    return OneRepMaxCalculator(BrzyckiStrategy())

@pytest.fixture
def epley_inverted_calculator():
    return InvertedCalculator(EpleyInvertedStrategy())

@pytest.fixture
def brzycki_inverted_calculator():
    return InvertedCalculator(BrzyckiInvertedStrategy())


# Tests for OneRepMaxCalculator
def test_epley_calculator_scalar(epley_calculator):
    result = epley_calculator.calculate(100, 10)
    assert result == pytest.approx(133.33, rel=1e-3)  # Expected based on Epley formula


# def test_brzycki_calculator_scalar(brzycki_calculator):
#     result = brzycki_calculator.calculate(100, 10)
#     assert result == pytest.approx(125.0, rel=1e-3)  # Expected based on Brzycki formula

# def test_calculator_vectorized(epley_calculator):
#     weights = np.array([100, 120])
#     reps = np.array([10, 8])
#     results = epley_calculator.calculate(weights, reps)
#     expected = np.array([133.33333333, 144.0])
#     np.testing.assert_allclose(results, expected, rtol=1e-3)

def test_calculator_mismatched_shapes(epley_calculator):
    weights = np.array([100, 120])
    reps = np.array([10])
    with pytest.raises(ValueError, match="Weight and reps must have the same shape when vectorized."):
        epley_calculator.calculate(weights, reps)

# def test_calculator_invalid_inputs(epley_calculator):
#     with pytest.raises(TypeError, match="Invalid input types.*"):
#         epley_calculator.calculate("100", 10)

# Tests for InvertedCalculator
# def test_epley_inverted_calculator_scalar(epley_inverted_calculator):
#     result = epley_inverted_calculator.calculate(133.33, 10, 2)
#     assert result == pytest.approx(91.489, rel=1e-3)  # Expected based on Epley inverted formula

# def test_brzycki_inverted_calculator_scalar(brzycki_inverted_calculator):
#     result = brzycki_inverted_calculator.calculate(125.0, 10, 2)
#     assert result == pytest.approx(82.086, rel=1e-3)  # Expected based on Brzycki inverted formula

# def test_inverted_calculator_vectorized(epley_inverted_calculator):
#     one_rm = np.array([133.33, 125.0])
#     reps = np.array([10, 8])
#     progression = np.array([2, 1.5])
#     results = epley_inverted_calculator.calculate(one_rm, reps, progression)
#     expected = np.array([91.489, 111.803])
#     np.testing.assert_allclose(results, expected, rtol=1e-3)

def test_inverted_calculator_mismatched_shapes(epley_inverted_calculator):
    one_rm = np.array([133.33, 125.0])
    reps = np.array([10])
    progression = np.array([2, 1.5])
    with pytest.raises(ValueError, match="One RM and reps must have the same shape when using vectors."):
        epley_inverted_calculator.calculate(one_rm, reps, progression)

def test_inverted_calculator_invalid_inputs(epley_inverted_calculator):
    with pytest.raises(TypeError, match="Invalid input types.*"):
        epley_inverted_calculator.calculate("133.33", 10, 2)

# # Additional tests for edge cases
# def test_zero_reps(epley_calculator):
#     with pytest.raises(ZeroDivisionError):
#         epley_calculator.calculate(100, 0)

# def test_negative_reps(brzycki_calculator):
#     with pytest.raises(ValueError, match="Reps cannot be negative."):
#         brzycki_calculator.calculate(100, -5)
