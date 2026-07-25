"""Get the bodyweight from the google sheet.
"""

from loguru import logger
import pandas as pd  # type: ignore[import-untyped]
from pprint import pformat
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
    return float(df["BODYWEIGHT_KG"].iloc[-1])


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
