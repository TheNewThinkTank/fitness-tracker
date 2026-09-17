"""Load and validate application configuration."""

from pathlib import Path

from dynaconf import Dynaconf, Validator  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[2]

settings = Dynaconf(
    settings_files=[str(PROJECT_ROOT / ".config/settings.toml")],
    envvar_prefix="FITNESS_TRACKER",
    environments=True,
    default_env="default",
    load_dotenv=True,
    merge_enabled=True,
)

settings.setenv("default")  # Ensure the correct environment is active
configured_data_dir = Path(settings.DATA_DIR).expanduser()
if not configured_data_dir.is_absolute():
    settings.set("DATA_DIR", str(PROJECT_ROOT / configured_data_dir))
settings.validators.register(
    Validator("DATA_DIR", must_exist=True, is_type_of=str),
    Validator("ATHLETE", default="default", is_type_of=str),
    Validator("ALLOWED_ORIGINS", default=[], is_type_of=list),
    Validator("API_TOKEN", default="", is_type_of=str),
)


def validate_settings() -> None:
    """Validate required settings and filesystem prerequisites."""
    settings.validators.validate()
    data_dir = Path(settings.DATA_DIR).expanduser()
    if not data_dir.is_dir():
        raise ValueError(f"DATA_DIR does not exist or is not a directory: {data_dir}")


def main() -> None:
    """Print key configuration values."""
    print(f"DATA_DIR: {Path(settings.DATA_DIR).expanduser().resolve()}")
    print(f"IMG_PATH: {Path(settings.IMG_PATH).expanduser().resolve()}")


if __name__ == "__main__":
    main()
