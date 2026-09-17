
from pathlib import Path

from src.utils.set_db_and_table import TinyDBSingleton  # type: ignore


def test_tiny_db_singleton(tmp_path: Path) -> None:
    first_path = str(tmp_path / "first.yml")
    second_path = str(tmp_path / "second.yml")
    instance1 = TinyDBSingleton(first_path)
    db1 = instance1.get_db()

    instance2 = TinyDBSingleton(first_path)
    db2 = instance2.get_db()

    assert instance1 is instance2
    assert db1 is db2

    instance3 = TinyDBSingleton(second_path)
    db3 = instance3.get_db()

    assert instance1 is not instance3
    assert db1 is not db3

    TinyDBSingleton.close_all()


# def test_set_db_and_table_real_data():
#     # Mock dependencies
#     with patch(
#         "src.utils.config_loader.ConfigLoader.load_env_variables",
#         return_value={"athlete": "test_athlete"}
#         ):
#         with patch("src.utils.config_loader.ConfigLoader.load_config", return_value={
#             "real_workout_database": "data/<YEAR>_workouts.yml",
#             "real_weight_table": "weight_training_log",
#             "training_catalogue": "src/utils/muscles_and_exercises.yaml",
#         }):
#             with patch("tinydb.TinyDB", MagicMock()):
#                 db, table, training_catalogue = set_db_and_table(
#                     "real",
#                     athlete="test_athlete",
#                     year=2023
#                     )

#                 # Verify the results
#                 assert db is not None
#                 assert table is not None
#                 assert training_catalogue == "src/utils/muscles_and_exercises.yaml"


# def test_set_db_and_table_simulated_data():
#     # Mock dependencies
#     with patch(
#         "src.utils.config_loader.ConfigLoader.load_env_variables",
#         return_value={"athlete": "test_athlete"}
#         ):
#         with patch("src.utils.config_loader.ConfigLoader.load_config", return_value={
#             "simulated_workout_database": "data/simulated_workouts.yml",
#             "simulated_weight_table": "simulated_weight_training_log",
#             "training_catalogue": "src/utils/muscles_and_exercises.yaml",
#         }):
#             with patch("tinydb.TinyDB", MagicMock()):
#                 db, table, training_catalogue = set_db_and_table(
#                     "simulated",
#                     athlete="test_athlete",
#                     year=2023
#                     )

#                 # Verify the results
#                 assert db is not None
#                 assert table is not None
#                 assert training_catalogue == "src/utils/muscles_and_exercises.yaml"


# def test_set_db_and_table_dev_environment():
#     # Mock dependencies
#     with patch(
#         "src.utils.config_loader.ConfigLoader.load_env_variables",
#         return_value={"athlete": "test_athlete"}
#         ):
#         with patch(
#             "src.utils.config_loader.ConfigLoader.load_config",
#             return_value={}
#             ):
#             with patch("tinydb.TinyDB", MagicMock()):
#                 db, table, training_catalogue = set_db_and_table(
#                     "real",
#                     athlete="test_athlete",
#                     year=2023,
#                     env="dev"
#                     )

#                 # Verify the results
#                 assert db is not None
#                 assert table is not None
#                 assert training_catalogue == "src/utils/muscles_and_exercises.yaml"


# def test_set_db_and_table_github_actions():
#     # Mock dependencies
#     with patch.dict("os.environ", {"GITHUB_ACTIONS": "true"}):
#         with patch(
#             "src.utils.config_loader.ConfigLoader.load_env_variables",
#             return_value={"athlete": "test_athlete"}
#             ):
#             with patch(
#                 "src.utils.config_loader.ConfigLoader.load_config",
#                 return_value={}
#                 ):
#                 with patch("tinydb.TinyDB", MagicMock()):
#                     db, table, training_catalogue = set_db_and_table(
#                         "real",
#                         athlete="test_athlete",
#                         year=2023
#                         )

#                     # Verify the results
#                     assert db is not None
#                     assert table is not None
#                     assert training_catalogue == "src/utils/muscles_and_exercises.yaml"
