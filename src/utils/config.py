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
settings.validators.validate()
# settings = settings.as_dict()


def main() -> None:
    """Load configuration and print it.
    """

    from pprint import pformat  # type: ignore
    from loguru import logger  # type: ignore

    # logger.debug(pformat(settings))
    logger.debug(pformat(settings.ATHLETE))
    logger.debug(pformat(settings.GOOGLE_DRIVE_DATA_PATH))

    # Access settings
    # DEBUG = settings.DEBUG
    # ATHLETE = settings.ATHLETE
    # logger.debug(f"DEBUG: {DEBUG}")
    # ATHLETE = settings.get("ATHLETE", "default_value")
    # logger.debug(f"ATHLETE: {ATHLETE}")


if __name__ == "__main__":
    main()
