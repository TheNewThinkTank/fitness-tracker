
import pytest
import numpy as np
from src.one_rep_max import (  # type: ignore
    EpleyStrategy,
    BrzyckiStrategy,
)
from src.one_rep_max_calc import (  # type: ignore
    OneRepMaxCalculator,
    EpleyInvertedStrategy,
    BrzyckiInvertedStrategy,
    InvertedCalculator,
)


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


# --- OneRepMaxCalculator ---

def test_epley_calculator_scalar(epley_calculator):
    # 100 * (1 + 10/30) = 133.333...
    assert epley_calculator.calculate(100, 10) == pytest.approx(133.33, rel=1e-3)


def test_brzycki_calculator_scalar(brzycki_calculator):
    # 100 * 36 / (37 - 10) = 133.333...
    assert brzycki_calculator.calculate(100, 10) == pytest.approx(133.33, rel=1e-3)


def test_calculator_vectorized(epley_calculator):
    weights = np.array([100, 120])
    reps = np.array([10, 8])
    results = epley_calculator.calculate(weights, reps)
    # 100*(1+10/30)=133.33, 120*(1+8/30)=152.0
    expected = np.array([133.333, 152.0])
    np.testing.assert_allclose(results, expected, rtol=1e-3)


def test_calculator_mismatched_shapes(epley_calculator):
    weights = np.array([100, 120])
    reps = np.array([10])
    with pytest.raises(ValueError, match="Weight and reps must have the same shape when vectorized."):
        epley_calculator.calculate(weights, reps)


def test_calculator_zero_reps_rejected(epley_calculator):
    with pytest.raises(ValueError):
        epley_calculator.calculate(100, 0)


def test_calculator_negative_reps_rejected(epley_calculator):
    with pytest.raises(ValueError):
        epley_calculator.calculate(100, -5)


# --- InvertedCalculator ---

def test_epley_inverted_calculator_scalar(epley_inverted_calculator):
    # log10(2) * 133.33 / (1 + 10/30)
    expected = np.log10(2) * 133.33 / (1 + 10 / 30)
    assert epley_inverted_calculator.calculate(133.33, 10, 2) == pytest.approx(expected, rel=1e-3)


def test_brzycki_inverted_calculator_scalar(brzycki_inverted_calculator):
    # log10(2) * 125.0 * (37 - 10) / 36
    expected = np.log10(2) * 125.0 * (37 - 10) / 36
    assert brzycki_inverted_calculator.calculate(125.0, 10, 2) == pytest.approx(expected, rel=1e-3)


def test_inverted_calculator_vectorized(epley_inverted_calculator):
    one_rm = np.array([133.33, 125.0])
    reps = np.array([10, 8])
    progression = np.array([2, 1.5])
    results = epley_inverted_calculator.calculate(one_rm, reps, progression)
    expected = np.log10(progression) * one_rm / (1 + reps / 30)
    np.testing.assert_allclose(results, expected, rtol=1e-3)


def test_inverted_calculator_mismatched_shapes(epley_inverted_calculator):
    one_rm = np.array([133.33, 125.0])
    reps = np.array([10])
    progression = np.array([2, 1.5])
    with pytest.raises(ValueError, match="One RM and reps must have the same shape when using vectors."):
        epley_inverted_calculator.calculate(one_rm, reps, progression)


def test_inverted_calculator_invalid_inputs(epley_inverted_calculator):
    with pytest.raises(TypeError, match="Invalid input types.*"):
        epley_inverted_calculator.calculate("133.33", 10, 2)
