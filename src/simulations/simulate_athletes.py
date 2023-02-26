"""Generate fictitious athletes."""

import os
from pathlib import Path

from faker import Faker

fake = Faker()  # Faker("it_IT")  # default: en_US

for _ in range(2):
    athlete = fake.name().replace(" ", "_").lower()
    print(athlete)
    Path(f"data/{athlete}").mkdir(parents=True, exist_ok=True)

    if not os.listdir(f"data/{athlete}"):
        print(f"data/{athlete} is empty! Creating .gitkeep ...")
        open(f"data/{athlete}/.gitkeep", "w", encoding="utf8")
