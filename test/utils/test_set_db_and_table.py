
from unittest.mock import patch, MagicMock
from src.utils.set_db_and_table import (  # type: ignore
    set_db_and_table,
    TinyDBSingleton
    )


def test_tiny_db_singleton():
    # Mock the TinyDB class and os.makedirs
    with patch("tinydb.TinyDB", MagicMock()), patch("os.makedirs", MagicMock()):
        # Create the first instance
        instance1 = TinyDBSingleton("dummy_path.yml")
        db1 = instance1.get_db()

        # Create the second instance with the same path
        instance2 = TinyDBSingleton("dummy_path.yml")
        db2 = instance2.get_db()

        # Ensure both instances are the same
        assert instance1 is instance2
        assert db1 is db2

        # Create a third instance with a different path
        instance3 = TinyDBSingleton("another_dummy_path.yml")
        db3 = instance3.get_db()

        # Ensure the third instance is different
        assert instance1 is not instance3
        assert db1 is not db3

        # Close the instances
        instance1.close()


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
