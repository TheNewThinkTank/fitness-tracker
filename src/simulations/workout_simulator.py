"""."""

import random
import pathlib
import json
import yaml
import numpy as np


class WorkoutSimulator:
    """Simulate a workout"""

    # available_splits = ["back", "chest", "legs", "shoulders"] # Define list of available muscle groups

    def __init__(self, workout_date: str, progress: int, training_catalogue: str, output_dir: str) -> None:
        self.workout_date: str = workout_date
        self.progress: int = progress
        self.training_catalogue: str = training_catalogue
        self.output_dir: str = output_dir
        self.split: str = random.choice(["back", "chest", "legs", "shoulders"])

    def get_available_exercises(self, split: str) -> list[dict[str, list[int]]]:
        """Fetch musclegroup-exercises catalogue, with weight-ranges.

        :return: List of available exercises for the given muscle group
        :rtype: list[dict]
        """

        with open(self.training_catalogue, "r") as rf:
            available_exercises: dict[str, list[dict[str, list[int]]]] = yaml.safe_load(rf)

        return available_exercises[split]


    def simulate_exercises(self) -> list[dict[str, list[int]]]:
        """Simulate data for exercises.

        :return: _description_
        :rtype: list[dict]
        """

        available_exercises: list[dict[str, list[int]]] = self.get_available_exercises(self.split)
        random.shuffle(available_exercises)

        return available_exercises[:random.randint(2, 6)]

    def calculate_weight(self, weight_range, actual_reps) -> str:
        """Simulate that higher reps leads to lower weights.
        choose weight from inverted 1RM estimate plus randomised progression.

        :param weight_range: _description_
        :type weight_range: _type_
        :param actual_reps: _description_
        :type actual_reps: _type_
        :return: _description_
        :rtype: str
        """

        weight_choice: float = weight_range[-1] * ((100 - actual_reps * 2.5) / 100) + np.log10(
            self.progress
        )

        # print(weight_range, actual_reps, self.progress, weight_choice)
        return f"{weight_choice:.2f} kg"

    def simulate_sets_reps_weight(self) -> dict:
        """Simulate data for sets, reps and weight.

        :return: _description_
        :rtype: dict
        """

        mapping: dict = {}
        for exercise in self.simulate_exercises():
            no_of_sets = random.randint(1, 6)
            for k, weight_range in exercise.items():
                mapping[k] = []
                for actual_set in range(1, no_of_sets + 1):
                    actual_reps = random.randint(1, 10)
                    actual_weight = self.calculate_weight(weight_range, actual_reps)
                    mapping[k].append(
                        {
                            "set_number": actual_set,
                            "reps": actual_reps,
                            "weight": actual_weight,
                        }
                    )

        return mapping

    def format_data(self) -> dict:
        """Prepare data format for JSON file.

        :return: _description_
        :rtype: dict
        """

        return {
            "date": self.workout_date,
            "split": self.split,
            "exercises": self.simulate_sets_reps_weight(),
        }

    def write_data(self) -> None:
        """Insert simulated, formatted data into JSON file."""

        date = self.format_data()["date"]
        p = pathlib.Path(self.output_dir)
        p.mkdir(parents=True, exist_ok=True)
        fn = f"simulated_training_log_{date}.json"
        filepath = p / fn
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(self.format_data(), f)
