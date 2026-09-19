"""Get the bodyweight from the google sheet.
"""

from __future__ import annotations

from pprint import pformat

import pandas as pd  # type: ignore[import-untyped]
from loguru import logger

from src.utils.config import settings
from src.utils.google_sheet import get_sheet


def get_bw(url: str | None = None) -> float:
    """Get the bodyweight from the published Google Sheets CSV.

    :param url: URL of the publicly-published CSV export. Defaults to
        ``settings["BODYWEIGHT_CSV_URL"]``. Override in tests.
    :type url: str | None, optional
    :return: Bodyweight in kg
    :rtype: float
    """
    resolved_url = url or settings["BODYWEIGHT_CSV_URL"]
    df = pd.read_csv(resolved_url)
    if df.empty:
        raise ValueError("Bodyweight data is empty.")

    bodyweight_column = next(
        (
            column
            for column in ("BODYWEIGHT_KG", "DAILY_BODYWEIGHT_KG")
            if column in df.columns
        ),
        None,
    )
    if bodyweight_column is None:
        raise ValueError(
            "Bodyweight CSV is missing a BODYWEIGHT_KG or DAILY_BODYWEIGHT_KG column."
        )

    latest_value = df[bodyweight_column].dropna().iloc[-1]

    return float(latest_value)


def main() -> None:
    """Get the bodyweight from the google sheet.
    """
    sheet = get_sheet(
        sheet_id=settings["BODYWEIGHT_SHEET_ID"],
        sheet_title="2023-2024",
    )
    logger.debug(pformat(sheet))
    logger.debug(pformat(get_bw()))


if __name__ == "__main__":
    main()
