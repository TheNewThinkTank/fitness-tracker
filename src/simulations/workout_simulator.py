
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from pathlib import Path
import random
import numpy as np
import yaml  # type: ignore


class ExerciseRepository:
    """Handles the loading of exercises from a YAML file."""

    def __init__(self, training_catalogue: str):
        self.training_catalogue = training_catalogue

    def get_exercises(self, split: str) -> list[dict[str, list[int]]]:
        with open(self.training_catalogue, "r") as rf:
            available_exercises = yaml.safe_load(rf)
        return available_exercises[split]


@dataclass
class ExerciseSelector:
    """Selects random exercises from the repository."""
    repository: ExerciseRepository
    split: str = field(default_factory=lambda: random.choice(["back", "chest", "legs", "shoulders"]))
    exercises: list = field(init=False)

    def __post_init__(self):
        self.exercises = self.select_random_exercises()

    def select_random_exercises(self) -> list[dict[str, list[int]]]:
        available_exercises = self.repository.get_exercises(self.split)
        random.shuffle(available_exercises)
        return available_exercises[:random.randint(2, 6)]


class WorkoutSimulator:
    """Simulates a workout based on selected exercises."""

    def __init__(self, exercises: list, progress: int):
        if progress < 0:
            raise ValueError("Progress must be greater than or equal to zero")
        self.exercises = exercises
        self.progress = progress
        self.exercise_mapping = self.generate_exercise_mapping()
        self.workout_data = self.simulate_workout_data()

    def _calculate_weight(self, weight_range, actual_reps) -> str:
        weight_choice = weight_range[-1] * ((100 - actual_reps * 2.5) / 100) + np.log10(self.progress)
        return f"{weight_choice:.2f} kg"

    def generate_exercise_mapping(self) -> dict:
        return {exercise_name: weight_range for exercise in self.exercises for exercise_name, weight_range in exercise.items()}

    def simulate_workout_data(self) -> dict[str, list[dict[str, str | int]]]:
        workout_data: dict[str, list[dict[str, str | int]]] = {}
        for exercise_name, weight_range in self.exercise_mapping.items():
            no_of_sets = random.randint(1, 6)
            workout_data[exercise_name] = []
            for actual_set in range(1, no_of_sets + 1):
                actual_reps = random.randint(1, 10)
                actual_weight = self._calculate_weight(weight_range, actual_reps)
                workout_data[exercise_name].append({"set_number": actual_set, "reps": actual_reps, "weight": actual_weight})
        return workout_data


class DataFormatter(ABC):
    """Abstract base class for formatting data."""
    @abstractmethod
    def format_data(self) -> dict:
        pass

    @abstractmethod
    def write_data(self) -> None:
        pass


# @dataclass
class JSONWorkoutFormatter(DataFormatter):

    def __init__(self, workout_date: str, output_dir: str, data: dict, split: str):
        self.workout_date = workout_date
        self.output_dir = Path(output_dir)  # Convert to Path object
        self.data = data
        self.split = split

    def format_data(self) -> dict:
        return {
            "date": self.workout_date,
            "split": self.split,
            "exercises": self.data,
        }

    def write_data(self):
        # Ensure the output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Construct the file path
        filepath = self.output_dir / f"simulated_training_log_{self.workout_date}.json"
        
        # Debug print statement
        print(f"Writing data to: {filepath}")

        # Write the data to the JSON file
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(self.format_data(), f, ensure_ascii=False, indent=4)


def main() -> None:
    from pprint import pprint as pp

    TRAINING_CATALOGUE = "src/simulations/muscles_and_exercises_weight_ranges.yaml"
    selection = ExerciseSelector(ExerciseRepository(TRAINING_CATALOGUE))
    simulated_workout = WorkoutSimulator(exercises=selection.exercises, progress=10)

    pp(simulated_workout.workout_data)

    # You can now easily change the formatter or add new ones
    formatter = JSONWorkoutFormatter(
        workout_date="2023-01-01",
        output_dir="data/simulated/",
        data=simulated_workout.workout_data,
        split=selection.split,
    )
    formatter.write_data()


if __name__ == "__main__":
    main()
