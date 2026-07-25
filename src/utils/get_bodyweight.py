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

    if "BODYWEIGHT_KG" not in df.columns:
        raise ValueError("Bodyweight CSV is missing the BODYWEIGHT_KG column.")

    latest_value = df["BODYWEIGHT_KG"].iloc[-1]
    if pd.isna(latest_value):
        raise ValueError("Latest bodyweight value is missing.")

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
