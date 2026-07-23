"""Loads configuration from environment and files.
"""

from dynaconf import Dynaconf  # type: ignore

settings = Dynaconf(
        settings_files=[".config/settings.toml"],
        # envvar_prefix="DYNACONF", # False # Optional: Prefix for environment variables
        environments=True,  # Enable environments (default, development, production)
        default_env="default",
        load_dotenv=True,  # Load .env file
        envvar_for_dynaconf=".env",  # Path to .env file relative to settings.toml
    )

settings.setenv("default")  # Ensure the correct environment is active


def validate_settings() -> None:
    """Run settings validation. Call this at app startup, not at import time."""
    settings.validators.validate()


def main() -> None:
    """Print key configuration values."""
    print(f"GOOGLE_DRIVE_DATA_PATH: {settings.GOOGLE_DRIVE_DATA_PATH}")
    print(f"IMG_PATH: {settings.IMG_PATH}")


if __name__ == "__main__":
    main()
