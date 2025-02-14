
from pprint import pprint as pp
import yaml


def load_yaml(file_name):
    training_catalogue = "docs/project_docs/exercises/"
    with open(training_catalogue + file_name + '.yaml', 'r') as file:
        return yaml.safe_load(file)


abs = load_yaml("abs")
back = load_yaml("back")
chest = load_yaml("chest")
arms = load_yaml("arms/arms")
legs = load_yaml("legs/legs")
shoulders = load_yaml("shoulders")

combined = {
    'exercises': [
        abs,
        back,
        chest,
        arms,
        legs,
        shoulders
        ]
}

pp(combined)

with open("docs/project_docs/exercises/muscles_and_exercises.yaml", 'w') as wf:
    yaml.dump(combined, wf, default_flow_style=False)
