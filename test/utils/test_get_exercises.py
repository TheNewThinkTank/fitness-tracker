
from unittest.mock import patch
import pytest


def test_get_available_exercises():
    # Mock data for the training catalogue
    mock_training_catalogue = {
        "Upper Body": ["pushup", "pullup", "bench press"],
        "Lower Body": ["squat", "deadlift", "lunges"],
    }

    # Mock the load_yaml_file function in the get_exercises module
    with patch(
        "src.utils.get_exercises.load_yaml_file",
        return_value=mock_training_catalogue
        ):
        from src.utils.get_exercises import get_available_exercises
        # Test for Upper Body split
        result = get_available_exercises("dummy_path.yaml", "Upper Body")
        assert result == ["pushup", "pullup", "bench press"]

        # Test for Lower Body split
        result = get_available_exercises("dummy_path.yaml", "Lower Body")
        assert result == ["squat", "deadlift", "lunges"]


def test_get_available_exercises_invalid_split():
    # Mock data for the training catalogue
    mock_training_catalogue = {
        "Upper Body": ["pushup", "pullup", "bench press"],
        "Lower Body": ["squat", "deadlift", "lunges"],
    }

    # Mock the load_yaml_file function in the get_exercises module
    with patch(
        "src.utils.get_exercises.load_yaml_file",
        return_value=mock_training_catalogue
        ):
        from src.utils.get_exercises import get_available_exercises
        # Test for an invalid split
        with pytest.raises(KeyError):
            get_available_exercises("dummy_path.yaml", "Invalid Split")
