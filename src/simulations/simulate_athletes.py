"""Generate fictitious athletes."""

import os
from pathlib import Path
from faker import Faker

fake = Faker()  # Faker("it_IT")  # default: en_US

NUM_ATHLETES = 2
DATA_DIR = "data"


def generate_athlete() -> str:
    """_summary_

    :return: _description_
    :rtype: str
    """

    athlete = fake.name().replace(" ", "_").lower()
    print(athlete)
    Path(os.path.join(DATA_DIR, athlete)).mkdir(parents=True, exist_ok=True)

    athlete_dir = os.path.join(DATA_DIR, athlete)
    if not os.listdir(athlete_dir):
        print(f"{athlete_dir} is empty! Creating .gitkeep ...")
        with open(os.path.join(athlete_dir, ".gitkeep"), "w", encoding="utf8") as f:
            f.write()

    return athlete


def main():
    """_summary_
    """

    for _ in range(NUM_ATHLETES):
        generate_athlete()


if __name__ == "__main__":
    main()
