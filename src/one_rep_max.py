
from abc import ABC, abstractmethod


class OneRepMaxStrategy(ABC):
    @abstractmethod
    def calculate(self, weight, reps):
        pass


class EpleyStrategy(OneRepMaxStrategy):
    def calculate(self, weight, reps):
        return weight * (1 + reps / 30)


class BrzyckiStrategy(OneRepMaxStrategy):
    def calculate(self, weight, reps):
        return weight * 36 / (37 - reps)


class AcsmStrategy(OneRepMaxStrategy):
    def calculate(self, weight, reps):
        denominator = (100 - reps * 2.5) / 100
        if denominator == 0:
            raise ValueError("The denominator is zero in ACSM formula")
        return weight / denominator
