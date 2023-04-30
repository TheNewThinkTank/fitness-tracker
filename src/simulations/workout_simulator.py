"""_summary_
"""

from dataclasses import dataclass, field
import json
import pathlib
import random

import numpy as np
import yaml


@dataclass
class ExerciseSelector:
    """_summary_
    """

    # Path to YAML file with available exercises and weight ranges
    training_catalogue: str
    split: str = random.choice(["back", "chest", "legs", "shoulders"])
    exercises: float = field(init=False)

    def _get_available_exercises(self, split: str) -> list[dict[str, list[int]]]:
        """Fetch musclegroup-exercises catalogue, with weight-ranges.

        :param split: _description_
        :type split: str
        :return: List of available exercises for the given muscle group
        :rtype: list[dict[str, list[int]]]
        """

        with open(self.training_catalogue, "r") as rf:
            available_exercises: dict[str, list[dict[str, list[int]]]] = yaml.safe_load(rf)

        return available_exercises[split]

    def select_random_exercises(self) -> list[dict[str, list[int]]]:
        """Simulate data for exercises.

        :return: _description_
        :rtype: list[dict[str, list[int]]]
        """

        available_exercises: list[dict[str, list[int]]] = self._get_available_exercises(self.split)
        random.shuffle(available_exercises)

        return available_exercises[:random.randint(2, 6)]

    def __post_init__(self):
        self.exercises = self.select_random_exercises()


@dataclass
class WorkoutSimulator:
    """Simulate a workout"""

    exercises: list
    progress: int  # Progress made since the last workout
    exercise_mapping: dict = field(init=False)
    workout_data: dict = field(init=False)

    def _calculate_weight(self, weight_range, actual_reps) -> str:
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

    def generate_exercise_mapping(self) -> dict:
        """Generate a mapping of exercises to weight ranges.

        :return: A dictionary mapping exercise names to weight ranges.
        :rtype: dict
        """

        exercise_mapping = {}
        for exercise in self.exercises:
            for exercise_name, weight_range in exercise.items():
                exercise_mapping[exercise_name] = weight_range

        return exercise_mapping

    def simulate_workout_data(self) -> dict:
        """Simulate data for sets, reps and weight for given exercises.

        :param exercise_mapping: A dictionary mapping exercise names to weight ranges.
        :type exercise_mapping: dict
        :return: A dictionary mapping exercise names to a list of sets, reps and weights.
        :rtype: dict
        """

        workout_data = {}

        for exercise_name, weight_range in self.exercise_mapping.items():
            no_of_sets = random.randint(1, 6)
            workout_data[exercise_name] = []
            for actual_set in range(1, no_of_sets + 1):
                actual_reps = random.randint(1, 10)
                actual_weight = self._calculate_weight(weight_range, actual_reps)

                workout_data[exercise_name].append(
                    {
                        "set_number": actual_set,
                        "reps": actual_reps,
                        "weight": actual_weight,
                    }
                )

        return workout_data
    
    def __post_init__(self):
        # Validate input
        if self.progress < 0:
            raise ValueError("Progress must be greater than or equal to zero")

        self.exercise_mapping = self.generate_exercise_mapping()
        self.workout_data = self.simulate_workout_data()


class WorkoutFormatter:
    """_summary_
    """

    def __init__(self, workout_date: str, output_dir: str, data: dict, split: str) -> None:
        """_summary_

        :param workout_date: Date of the workout in "YYYY-MM-DD" format
        :type workout_date: str
        :param output_dir: Path to directory to output the simulated workout JSON file
        :type output_dir: str
        :raises ValueError: _description_
        """

        # Validate input
        try:
            assert len(workout_date) == 10
            int(workout_date[:4])
            int(workout_date[5:7])
            int(workout_date[8:10])
        except AssertionError:
            raise ValueError("Invalid workout date")
        
        self.workout_date: str = workout_date
        self.output_dir: str = output_dir
        self.data: dict = data
        self.split: dict = split

    def format_data(self) -> dict:
        """Prepare data format for JSON file.

        :return: _description_
        :rtype: dict
        """

        return {
            "date": self.workout_date,
            "split": self.split,
            "exercises": self.data,
        }

    def write_data(self) -> None:
        """Insert simulated, formatted data into JSON file.
        """

        try:
            date = self.format_data()["date"]
        except KeyError as e:
            print(f"Error: {e} not found in data")
            return

        p = pathlib.Path(self.output_dir)
        try:
            p.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error: {e}")
            return

        fn = f"simulated_training_log_{date}.json"
        filepath = p / fn
        try:
            with filepath.open("w", encoding="utf-8") as f:
                json.dump(self.format_data(), f, indent=4)
        except IOError as e:
            print(f"Error: {e}")
            return


def main():
    """_summary_
    """

    from pprint import pprint as pp

    TRAINING_CATALOGUE: str = "src/simulations/muscles_and_exercises_weight_ranges.yaml"
    # OUTPUT_DIR: str = "data/simulated/"
    # WORKOUT_DATE: str = "2023-01-01"

    selection = ExerciseSelector(TRAINING_CATALOGUE)

    simulated_workout = WorkoutSimulator(
        exercises=selection.exercises,
        progress=10,
        )

    pp(simulated_workout.workout_data)

    # formatter = WorkoutFormatter(
    #     workout_date=WORKOUT_DATE,
    #     output_dir=OUTPUT_DIR,
    #     data=data,
    #     split=selection.split,
    # )

    # pp(formatter.format_data())
    # formatter.write_data()


if __name__ == "__main__":
    main()
