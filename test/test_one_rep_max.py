
import pytest
import numpy as np
from src.one_rep_max import EpleyStrategy, BrzyckiStrategy, ACSMStrategy


@pytest.fixture
def epley_strategy():
    return EpleyStrategy()


@pytest.fixture
def brzycki_strategy():
    return BrzyckiStrategy()


@pytest.fixture
def acsm_strategy():
    return ACSMStrategy()


class TestEpleyStrategy:

    def test_estimate_scalar(self, epley_strategy):
        assert epley_strategy.estimate(100, 10) == 133.33333333333331

    def test_estimate_array(self, epley_strategy):
        weights = np.array([100, 150])
        reps = np.array([10, 5])
        expected = weights * (1 + reps / 30)
        np.testing.assert_allclose(epley_strategy.estimate(weights, reps), expected)


class TestBrzyckiStrategy:

    def test_estimate_scalar(self, brzycki_strategy):
        assert brzycki_strategy.estimate(100, 10) == pytest.approx(133.33333333333334)

    def test_estimate_array(self, brzycki_strategy):
        weights = np.array([100, 150])
        reps = np.array([10, 5])
        expected = weights * 36 / (37 - reps)
        np.testing.assert_allclose(brzycki_strategy.estimate(weights, reps), expected)


class TestACSMStrategy:

    def test_estimate_scalar(self, acsm_strategy):
        assert acsm_strategy.estimate(100, 10) == pytest.approx(133.33333333333334)

    def test_estimate_array(self, acsm_strategy):
        weights = np.array([100, 150])
        reps = np.array([10, 5])
        expected = weights / ((100 - reps * 2.5) / 100)
        np.testing.assert_allclose(acsm_strategy.estimate(weights, reps), expected)

    def test_estimate_zero_denominator(self, acsm_strategy):
        weights = np.array([100, 150])
        reps = np.array([40, 45])  # Causes denominator to be zero
        with pytest.raises(ValueError, match="denominator is zero in ACSM formula"):
            acsm_strategy.estimate(weights, reps)
