"""Generate fictitious people."""

import os
from pathlib import Path
from faker import Faker


def generate_person(fake, data_dir:str = "data") -> str:
    """_summary_

    :return: _description_
    :rtype: str
    """

    person = fake.name().replace(" ", "_").lower()
    print(person)
    Path(os.path.join(data_dir, person)).mkdir(parents=True, exist_ok=True)

    person_dir = os.path.join(data_dir, person)
    if not os.listdir(person_dir):
        print(f"{person_dir} is empty! Creating .gitkeep ...")
        with open(os.path.join(person_dir, ".gitkeep"), "w", encoding="utf8") as f:
            f.write("")

    return person


def generate_people(locale:str="en_US", num_people:int=2) -> None:
    """_summary_
    """

    fake = Faker(locale)  # locale = "it_IT" # default: "en_US"

    for _ in range(num_people):
        generate_person(fake)


if __name__ == "__main__":
    generate_people()
