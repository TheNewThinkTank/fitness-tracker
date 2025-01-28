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
config_data = settings.as_dict()


def main() -> None:
    """Load configuration and print it.
    """

    from pprint import pprint as pp

    pp(config_data)

    # Access settings
    # DEBUG = settings.DEBUG
    # ATHLETE = settings.ATHLETE

    # print(f"DEBUG: {DEBUG}")
    # print(f"ATHLETE: {ATHLETE}")

    # ATHLETE = settings.get("ATHLETE", "default_value")
    # print(f"ATHLETE: {ATHLETE}")


if __name__ == "__main__":
    main()
