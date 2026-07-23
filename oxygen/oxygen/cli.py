#!/usr/bin/env python3

"""This CLI program provides a convenient way to manage and visualize workout data.
By using the provided commands, you can insert data, prepare figures,
and open generated images for analysis and review.

Commands:

1. Insert Workout Data

Use the insert command to insert workout data into the database.

python cli.py insert --workout-date YYYY-MM-DD --file-format FORMAT

--workout-date (-d): Specify the workout date (default: today).
--file-format (-f): Specify the file format (yml, json, csv) (default: yml).

Example:
python cli.py insert --workout-date 2023-01-01 --file-format yml

2. Prepare Figures

Use the prepare_figures command to prepare figures for the specified year and month.

python cli.py prepare_figures --year YEAR --month MONTH

--year (-y): Specify the year to plot (default: current year).
--month (-m): Specify the month to plot (default: current month).

Example:
python cli.py prepare_figures --year 2023 --month January

3. Open Images

Use the open_images command to open generated workout images for the specified year and month.

python cli.py open_images --year YEAR --month MONTH

--year (-y): Specify the year of the images to open (default: current year).
--month (-m): Specify the month of the images to open (default: current month).

python cli.py open_images --year 2023 --month January

4. Show Help

Use the show_help command to display the help message for the CLI.

python cli.py show_help
"""

from datetime import datetime as dt
import os
import subprocess
import click
from loguru import logger  # type: ignore
from src.utils.config import settings  # type: ignore
from src.crud.insert import insert_specific_log, WorkoutDate  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.combined_metrics.combined_metrics import run as combined_metrics_run  # type: ignore


@click.group()
def cli():
    """Fitness Tracker CLI."""
    pass


@cli.command()
@click.option(
    "--workout-date",
    "-d",
    default=dt.now().strftime("%Y-%m-%d"),
    help="Specify the workout date (default: today).",
)
@click.option(
    "--file-format",
    "-f",
    default="yml",
    type=click.Choice(["yml", "json"]),
    help="Specify the file format (default: yml).",
)
def insert(workout_date, file_format):
    """Insert workout data into the database."""
    try:
        logger.info(f"Inserting data for {workout_date} with format {file_format}.")
        _, table, _ = set_db_and_table(datatype="real")
        insert_specific_log(WorkoutDate(workout_date), table, file_format)
        logger.info("Data inserted successfully.")
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--year",
    "-y",
    default=dt.now().year,
    type=int,
    help="Specify the year to plot.",
)
@click.option(
    "--month",
    "-m",
    default=dt.now().strftime("%B"),
    help="Specify the month to plot.",
)
def prepare_figures(year, month):
    """Prepare figures for the specified year and month."""
    try:
        logger.info(f"Preparing figures for {year} {month}.")
        combined_metrics_run(year_to_plot=str(year), month_to_plot=month)
        logger.info("Figures prepared successfully.")
    except Exception as e:
        logger.error(f"Error preparing figures: {e}")
        raise SystemExit(1)


@cli.command()
@click.pass_context
@click.option(
    "--year",
    "-y",
    default=dt.now().year,
    type=int,
    help="Specify the year of the images to open.",
)
@click.option(
    "--month",
    "-m",
    default=dt.now().strftime("%B"),
    help="Specify the month of the images to open.",
)
def open_images(ctx, year, month):
    """Open generated workout images."""

    img_path = f"{settings['IMG_PATH']}{year}/{month}/"

    try:
        logger.info(f"Opening images for {year} {month}.")
        for img_file in [
            f"{img_path}{year}_workout_frequency.png",
            f"{img_path}workout_duration_{month}_{year}.png",
        ]:
            if os.path.exists(img_file):
                subprocess.run(["open", img_file], check=True)
            else:
                logger.warning(f"{img_file} not found.")
        logger.info("Images opened successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error opening images: {e}")
        raise SystemExit(1)


@cli.command()
@click.pass_context
def show_help(ctx):
    """Show the help message."""
    click.echo(cli.get_help(ctx))


if __name__ == "__main__":
    cli()
