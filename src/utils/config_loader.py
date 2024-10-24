
import os
import yaml  # type: ignore
from dotenv import load_dotenv


class ConfigLoader:
    """Handles loading configuration from environment and files."""

    @staticmethod
    def load_env_variables() -> dict:
        """Loads environment variables."""
        load_dotenv()
        return {
            "user": os.environ["USER"],
            "athlete": os.environ["ATHLETE"],
            "email": os.environ["EMAIL"]
            }

    @staticmethod
    def load_config(
        user: str,
        athlete: str,
        email: str,
        file_path: str="./.config/config.yml"
        ) -> dict:
        """Loads configuration from a YAML file and replaces placeholders."""
        with open(file_path, "r") as rf:
            data = yaml.safe_load(rf)

            google_drive_data_path = (
                data["google_drive_data_path"]
                .replace("<USER>", user)
                .replace("<EMAIL>", email)
            )

            data["google_drive_data_path"] = google_drive_data_path

            data["real_workout_database"] = (
                data["real_workout_database"]
                .replace("<GOOGLE_DRIVE_DATA_PATH>", google_drive_data_path)
                .replace("<ATHLETE>", athlete)
            )

        return data


def main():
    from pprint import pprint as pp

    env_vars = ConfigLoader.load_env_variables()

    config = ConfigLoader.load_config(
        env_vars["user"],
        env_vars["athlete"],
        env_vars["email"],
        "./.config/config.yml"
    )

    # file = config["real_workout_database"]
    pp(config)


if __name__ == "__main__":
    main()
