from test.conftest import src
from src.helpers.get_workout_duration import get_workout_duration
from src.helpers.config_loader import ConfigLoader  # type: ignore


def test_get_year_and_week():

    # env_vars = ConfigLoader.load_env_variables()
    # config = ConfigLoader.load_config(
    #     athlete=env_vars["athlete"],
    #     user=env_vars["user"],
    #     email=env_vars["email"],
    # )

    assert (
        get_workout_duration("14:45", "15:10") == 25
    )
