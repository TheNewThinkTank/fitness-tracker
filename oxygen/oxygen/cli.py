"""Oxygen: validated workout imports, plots, and a portable CLI workflow."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from functools import wraps
import importlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tomllib
from typing import Any, Callable
from uuid import uuid5

import click
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
import yaml

from src.common.params import PlotParams
from src.common.workout_types import WORKOUT_ID_NAMESPACE, WorkoutData, get_workout_id, parse_workout_date
from src.crud.insert import _load_workout_record
from src.utils.config import settings
from src.utils.set_db_and_table import TinyDBSingleton, get_available_years, get_database_path, set_db_and_table
from src.utils.workout_repository import WorkoutRepository

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")


@dataclass(frozen=True)
class Configuration:
    data_dir: Path
    image_dir: Path


@dataclass(frozen=True)
class WorkoutFile:
    path: Path
    date: date
    record: dict[str, Any]


class OxygenGroup(click.Group):
    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        return super().get_command(ctx, cmd_name.replace("_", "-"))


def _errors(callback: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(callback)
    def checked(*arguments: Any, **options: Any) -> Any:
        try:
            return callback(*arguments, **options)
        except click.ClickException:
            raise
        except (OSError, ValueError, yaml.YAMLError, subprocess.SubprocessError) as error:
            raise click.ClickException(str(error)) from error
    return checked


def _dates(ctx: click.Context, parameter: click.Parameter, values: tuple[str, ...]) -> tuple[date, ...]:
    parsed = []
    for value in values or (date.today().isoformat(),):
        for entry in value.split(","):
            try:
                performed = parse_workout_date(entry.strip())
                if not 1900 <= performed.year <= 2100:
                    raise ValueError("Workout dates must be between 1900 and 2100")
            except ValueError as error:
                raise click.BadParameter(str(error), ctx=ctx, param=parameter) from error
            if performed not in parsed:
                parsed.append(performed)
    return tuple(parsed)


def _month(ctx: click.Context, parameter: click.Parameter, value: str) -> str:
    candidate = value.strip().casefold()
    for number, name in enumerate(MONTHS, start=1):
        if candidate in (name.casefold(), name[:3].casefold(), str(number), f"{number:02d}"):
            return name
    raise click.BadParameter("Use a month name, abbreviation, or number between 1 and 12", ctx=ctx, param=parameter)


def _date_options(callback: Callable[..., Any]) -> Callable[..., Any]:
    callback = click.option("--workout-number", "-w", type=click.IntRange(min=1), help="Import only this numbered workout.")(callback)
    callback = click.option("--file-format", "-f", type=click.Choice(["yml", "json"], case_sensitive=False), default="yml", show_default=True)(callback)
    return click.option("--workout-date", "--dates", "-d", "dates", multiple=True, callback=_dates, help="ISO date; repeat or separate dates with commas. Defaults to today.")(callback)


def _period_options(callback: Callable[..., Any]) -> Callable[..., Any]:
    callback = click.option("--month", "-m", callback=_month, default=lambda: MONTHS[date.today().month - 1], show_default="current month")(callback)
    return click.option("--year", "-y", type=click.IntRange(1900, 2100), default=lambda: date.today().year, show_default="current year")(callback)


def _check_exercise_names(record: dict[str, Any]) -> None:
    for exercise in record.get("exercises") or {}:
        if any(ord(character) < 32 or character in '/\\:*?"<>|' for character in exercise):
            raise ValueError(f"Unsafe exercise name for figure output: {exercise!r}")


def _discover(configuration: Configuration, performed: date, file_format: str, workout_number: int | None) -> list[Path]:
    base = configuration.data_dir / "log_archive" / file_format.upper() / str(performed.year) / MONTHS[performed.month - 1]
    if not base.resolve().is_relative_to(configuration.data_dir):
        raise ValueError("Workout archive path escapes the configured data directory")
    pattern = re.compile(r".*training_log_" + re.escape(performed.isoformat()) + r"(?:_([1-9][0-9]*))?\." + file_format + r"$")
    matched = []
    for path in base.rglob(f"*training_log_{performed.isoformat()}*.{file_format}"):
        match = pattern.fullmatch(path.name)
        if match is None or not path.is_file():
            continue
        number = int(match.group(1) or 1)
        if workout_number is not None and number != workout_number:
            continue
        if not path.resolve().is_relative_to(base.resolve()):
            raise ValueError(f"Workout file escapes its archive directory: {path}")
        matched.append((number, str(path), path))
    if not matched:
        raise FileNotFoundError(f"No {file_format} workout files found for {performed} in {base}")
    return [entry[2] for entry in sorted(matched)]


def _plan(configuration: Configuration, dates: tuple[date, ...], file_format: str, workout_number: int | None) -> list[WorkoutFile]:
    if not configuration.data_dir.is_dir():
        raise FileNotFoundError(f"Data directory does not exist: {configuration.data_dir}")
    planned = []
    identifiers = set()
    for performed in dates:
        for path in _discover(configuration, performed, file_format, workout_number):
            try:
                record = _load_workout_record(path, file_format, expected_date=performed.isoformat())
                _check_exercise_names(record)
            except (OSError, ValueError, yaml.YAMLError) as error:
                raise ValueError(f"Cannot import {path}: {error}") from error
            identifier = str(record.get("id") or uuid5(WORKOUT_ID_NAMESPACE, "oxygen:" + path.relative_to(configuration.data_dir).as_posix()))
            if identifier in identifiers:
                raise ValueError(f"Multiple input files contain workout ID {identifier}")
            identifiers.add(identifier)
            planned.append(WorkoutFile(path, performed, {**record, "id": identifier}))
    return planned


def _existing() -> dict[str, dict[str, Any]]:
    records = {}
    for year in get_available_years():
        path = get_database_path("real", year=year)
        with path.open(encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        if not isinstance(payload, dict) or not isinstance(payload.get(str(settings.REAL_WEIGHT_TABLE), {}), dict):
            raise ValueError(f"Invalid workout archive: {path}")
        for document_id, record in payload.get(str(settings.REAL_WEIGHT_TABLE), {}).items():
            if not isinstance(record, dict):
                continue
            identifier = str(get_workout_id(record, year, int(document_id)))
            if identifier in records:
                raise ValueError(f"Duplicate existing workout ID: {identifier}")
            records[identifier] = {**record, "id": identifier}
    return records


def _import(planned: list[WorkoutFile], *, dry_run: bool) -> None:
    existing = _existing()
    pending: dict[int, list[dict[str, Any]]] = defaultdict(list)
    skipped = 0
    for workout in planned:
        previous = existing.get(workout.record["id"])
        if previous is not None:
            previous = WorkoutData.model_validate(previous).model_dump(mode="json", exclude_none=True)
            current = WorkoutData.model_validate(workout.record).model_dump(mode="json", exclude_none=True)
            if previous != current:
                raise ValueError(f"Workout ID {workout.record['id']} conflicts with existing data: {workout.path}")
            skipped += 1
        else:
            pending[workout.date.year].append(workout.record)
    for workout in planned:
        action = "Skip" if workout.record["id"] in existing else "Would import" if dry_run else "Import"
        click.echo(f"{action}: {workout.path} -> {get_database_path('real', year=workout.date.year)}")
    if not dry_run:
        for year, records in pending.items():
            _, table, _ = set_db_and_table("real", year=year)
            table.insert_multiple(records)
    count = sum(len(records) for records in pending.values())
    click.echo(f"{'Dry run: ' if dry_run else ''}{count} {'to import' if dry_run else 'imported'}, {skipped} skipped")


def _plotting() -> Any:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        return importlib.import_module("src.combined_metrics.combined_metrics")
    except ImportError as error:
        raise click.ClickException("Plotting dependencies are unavailable. Run 'poetry install --with analytics', or use 'run --no-figures'.") from error


def _render(table: Any, year: int, month: str, image_dir: Path) -> None:
    plotting = _plotting()
    params = PlotParams(table=table, year=str(year), img_path=str(image_dir))
    try:
        plotting.plot_frequency(params)
        plotting.plot_duration(PlotParams(table=table, year=str(year), month=month, img_path=str(image_dir)))
        plotting.plot_duration_volume_1rm(params)
    finally:
        plotting.plt.close("all")


def _prepare(configuration: Configuration, year: int, month: str) -> list[Path]:
    repository = WorkoutRepository()
    try:
        documents = repository.documents(year)
    except FileNotFoundError as error:
        raise click.ClickException(f"No workout data for {year}") from error
    if not documents:
        raise click.ClickException(f"No workout data for {year}")
    for _, record in documents:
        _check_exercise_names(record)
    with TinyDB(storage=MemoryStorage) as database, TemporaryDirectory(prefix="oxygen-figures-") as temporary:
        table = database.table(str(settings.REAL_WEIGHT_TABLE))
        table.insert_multiple([record for _, record in documents])
        staging = Path(temporary)
        _render(table, year, month, staging)
        figures = sorted(staging.rglob("*.png"))
        if not figures:
            raise click.ClickException(f"No figures could be generated for {month} {year}")
        outputs = []
        for source in figures:
            relative = source.relative_to(staging)
            if relative.parts[0] == "all_years":
                relative = Path(str(year), *relative.parts[1:])
            destination = configuration.image_dir / relative
            if not destination.resolve().is_relative_to(configuration.image_dir):
                raise ValueError(f"Figure output escapes the configured image directory: {destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=destination.parent, prefix=".oxygen-", suffix=".png", delete=False) as handle:
                temporary_path = Path(handle.name)
            try:
                shutil.copyfile(source, temporary_path)
                os.replace(temporary_path, destination)
            finally:
                temporary_path.unlink(missing_ok=True)
            click.echo(f"Figure: {destination}")
            outputs.append(destination)
        return outputs


def _open(paths: list[Path]) -> None:
    if not paths:
        raise click.ClickException("No generated images found; run prepare-figures first")
    if sys.platform == "win32":
        startfile = getattr(os, "startfile", None)
        if startfile is None:
            raise click.ClickException("The system image opener is unavailable")
        for path in paths:
            startfile(str(path))
    else:
        opener = shutil.which("open" if sys.platform == "darwin" else "xdg-open")
        if opener is None:
            raise click.ClickException("No desktop image opener found; use the printed paths or run with --no-open")
        for path in paths:
            subprocess.run([opener, str(path)], check=True)


@click.group(cls=OxygenGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="fitness-tracker", prog_name="oxygen")
@click.option("--config", "-c", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Oxygen TOML configuration file.")
@click.option("--data-dir", type=click.Path(file_okay=False, path_type=Path), help="Override the raw-log and year-archive directory.")
@click.option("--image-dir", type=click.Path(file_okay=False, path_type=Path), help="Override the generated image directory.")
@click.pass_context
@_errors
def cli(ctx: click.Context, config: Path | None, data_dir: Path | None, image_dir: Path | None) -> None:
    """Fitness Tracker imports and plots without shell scripts."""
    configured: dict[str, str] = {}
    if config is not None:
        with config.open("rb") as handle:
            values = tomllib.load(handle)
        values = values.get("oxygen", values)
        if not isinstance(values, dict) or set(values) - {"data_dir", "image_dir"} or any(not isinstance(value, str) for value in values.values()):
            raise ValueError("Oxygen configuration accepts only string data_dir and image_dir settings")
        configured = values
        if data_dir is None and "data_dir" in configured:
            data_dir = config.resolve().parent / Path(configured["data_dir"]).expanduser()
        if image_dir is None and "image_dir" in configured:
            image_dir = config.resolve().parent / Path(configured["image_dir"]).expanduser()
    original = {key: settings.get(key) for key in ("DATA_DIR", "IMG_PATH", "REAL_WORKOUT_DATABASE")}

    def restore_settings() -> None:
        for key, value in original.items():
            settings.set(key, value)

    ctx.call_on_close(restore_settings)
    ctx.call_on_close(TinyDBSingleton.close_all)
    root = Path(data_dir or settings.DATA_DIR).expanduser().resolve()
    images = Path(image_dir or (root / "img" if data_dir is not None else str(settings.IMG_PATH))).expanduser().resolve()
    if data_dir is not None:
        settings.set("DATA_DIR", str(root))
        settings.set("REAL_WORKOUT_DATABASE", str(root / "<YEAR>_workouts.yml"))
    settings.set("IMG_PATH", str(images))
    ctx.obj = Configuration(root, images)


@cli.command()
@_date_options
@click.option("--dry-run", is_flag=True, help="Validate and show changes without writing archives.")
@click.pass_obj
@_errors
def insert(configuration: Configuration, dates: tuple[date, ...], file_format: str, workout_number: int | None, dry_run: bool) -> None:
    """Import every matching log for the selected dates, without plotting."""
    _import(_plan(configuration, dates, file_format, workout_number), dry_run=dry_run)


@cli.command()
@_date_options
@click.option("--dry-run", is_flag=True, help="Validate imports and show plot periods without writing files.")
@click.option("--figures/--no-figures", default=True, show_default=True)
@click.option("--open/--no-open", "open_after", default=False, show_default=True, help="Open generated images using the desktop viewer.")
@click.pass_obj
@_errors
def run(configuration: Configuration, dates: tuple[date, ...], file_format: str, workout_number: int | None, dry_run: bool, figures: bool, open_after: bool) -> None:
    """Import logs and generate figures once per distinct year/month."""
    if open_after and not figures:
        raise click.UsageError("--open requires --figures")
    planned = _plan(configuration, dates, file_format, workout_number)
    if figures and not dry_run:
        _plotting()
    _import(planned, dry_run=dry_run)
    outputs = []
    if figures:
        periods = dict.fromkeys((performed.year, MONTHS[performed.month - 1]) for performed in dates)
        for year, month in periods:
            if dry_run:
                click.echo(f"Would prepare figures: {month} {year}")
            else:
                outputs.extend(_prepare(configuration, year, month))
    if open_after and not dry_run:
        _open(list(dict.fromkeys(outputs)))


@cli.command("prepare-figures")
@_period_options
@click.pass_obj
@_errors
def prepare_figures(configuration: Configuration, year: int, month: str) -> None:
    """Generate saved PNGs from archives and local SQLite overlays."""
    _prepare(configuration, year, month)


@cli.command("open-images")
@_period_options
@click.pass_obj
@_errors
def open_images(configuration: Configuration, year: int, month: str) -> None:
    """Open existing figures without importing or plotting data."""
    directory = configuration.image_dir / str(year)
    candidates = [directory / f"{year}_workout_frequency.png", directory / f"workout_duration_{month}_{year}.png", *sorted(directory.glob("workout_duration_volume_1rm_*.png"))]
    _open([path for path in candidates if path.is_file()])


@cli.command("show-help")
@click.pass_context
def show_help(ctx: click.Context) -> None:
    """Show the top-level command help."""
    click.echo(cli.get_help(ctx.parent or ctx))


if __name__ == "__main__":
    cli()
