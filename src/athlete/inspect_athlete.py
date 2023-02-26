"""."""

import pandas as pd  # type: ignore

from athlete import Athlete
from vo2_max_data import vo2_max_data
from athletes_info import athletes_info


def update_readme(metric, unit):
    with open("README_test.md", "r") as rf:
        contents = rf.readlines()
        for num, line in enumerate(contents):
            if "## Examples" in line:
                contents.insert(num + 1, "### Fitness Metrics<br>")
                contents.insert(num + 2, f"VO2-Max: {metric} {unit}")

    with open("README_test.md", "w") as wf:
        contents = "".join(contents)
        wf.write(contents)


def create_athletes():
    """."""

    return [
        Athlete(
            name=name,
            gender=athletes_info[name].get("gender", "Gender not specified"),
            dob=athletes_info[name].get("dob", "Date of birth is missing!"),
            height=athletes_info[name].get("height", "Height is missing!"),
            bodyweight=athletes_info[name].get("bodyweight", "Bodyweight is missing!"),
            hr_rest=athletes_info[name].get("hr_rest", ""),
            sport=athletes_info[name].get("sport", ""),
            death_date=athletes_info[name].get("death_date", ""),
        )
        for name in athletes_info.keys()
    ]


def compare_athletes(athletes):
    print("\nSorted by BMI:")
    bmi_ordered = sorted(athletes, key=lambda x: x.get_bmi())
    for athlete in bmi_ordered:
        print(athlete.name)

    print("\nSorted by age:")
    age_ordered = sorted(athletes, key=lambda x: x.get_age())
    for athlete in age_ordered:
        print(athlete.name)

    print("\nGroup by sports")
    sports_ordered = sorted(athletes, key=lambda x: x.sport)
    for athlete in sports_ordered:
        print(athlete.sport)
        print(athlete.name)
        print("\n")


def get_age_ranges(df_males, df_females) -> list:
    # age ranges must be identical for both genders
    assert all(df_males.columns[2:] == df_females.columns[2:])
    return [
        range(int(i.split("-")[0]), int(i.split("-")[1]) + 1)
        for i in df_males.columns[2:]
    ]


def has_age_in_range(age, age_ranges):
    if 20 > age or 79 < age:
        return False
    for age_range in age_ranges:
        if age in age_range:
            return True
    return False


def get_age_range(age, age_ranges):
    for age_range in age_ranges:
        if age in age_range:
            return age_range


def get_category(df, gender_col, age_range, vo2_max):
    """."""

    age_interval = f"{age_range[0]}-{age_range[-1]}"
    category_index = (df[age_interval] - vo2_max).abs().argsort()[:1]
    category_val = df.iloc[category_index][gender_col]

    return category_val[0]


def main():
    """."""

    df_males = pd.DataFrame(data=vo2_max_data["M"])
    df_females = pd.DataFrame(data=vo2_max_data["F"])
    age_ranges = get_age_ranges(df_males, df_females)
    athletes = create_athletes()
    # compare_athletes(athletes)

    for athlete in athletes:
        age = athlete.get_age()
        df = df_males if athlete.gender == "M" else df_females
        gender_col = "Males" if athlete.gender == "M" else "Females"
        print(f"\nAthlete: {athlete.name}. Age: {age}")

        if not athlete.hr_rest:
            continue

        vo2_max = athlete.get_vo2_max()
        # update_readme(vo2_max, "mL/kg/min")
        print(f"Resting heart rate: {athlete.hr_rest}")
        print(f"VO2-MAX: {vo2_max} mL/kg/min")

        if not has_age_in_range(age, age_ranges):
            continue

        age_range = get_age_range(age, age_ranges)
        category = get_category(df, gender_col, age_range, vo2_max)
        print(f"Athlete VO2-MAX category: {category}")


if __name__ == "__main__":
    main()
