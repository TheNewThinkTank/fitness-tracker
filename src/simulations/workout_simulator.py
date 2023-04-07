"""."""

import random
import pathlib
import json
import yaml


class WorkoutSimulator:
    """Simulate a workout"""

    splits: list[str] = ["back", "chest", "legs", "shoulders"]
    training_catalogue: str = "src/simulations/muscles_and_exercises_weight_ranges.yaml"
    output_dir: str = "data/simulated/"

    def __init__(self, workout_date: str, progress: int) -> None:
        self.workout_date = workout_date
        self.progress = progress
        self.split = random.choice(self.splits)

    def get_available_exercises(self) -> list[dict]:
        """Fetch musclegroup-exercises catalogue, with weight-ranges.

        :return: _description_
        :rtype: list[dict]
        """

        with open(self.training_catalogue, "r") as rf:
            available_exercises = yaml.safe_load(rf)  # yaml.load(rf, Loader=yaml.FullLoader)

        return available_exercises[self.split]

    def simulate_exercises(self) -> list[dict]:
        """Simulate data for exercises.

        :return: _description_
        :rtype: list[dict]
        """

        random.shuffle(self.get_available_exercises())

        return self.get_available_exercises()[:random.randint(2, 6)]

    def high_reps_low_weight(self, weight_range, actual_reps) -> str:
        """Simulate that higher reps leads to lower weights.
        choose weight from inverted 1RM estimate plus randomised progression.

        :param weight_range: _description_
        :type weight_range: _type_
        :param actual_reps: _description_
        :type actual_reps: _type_
        :return: _description_
        :rtype: str
        """

        weight_choice = weight_range[-1] * ((100 - actual_reps * 2.5) / 100) + np.log10(
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
                    actual_weight = self.high_reps_low_weight(weight_range, actual_reps)
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
