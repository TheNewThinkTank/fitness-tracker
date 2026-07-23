"""Get the bodyweight from the google sheet.
"""

from loguru import logger  # type: ignore
import pandas as pd  # type: ignore
from pprint import pformat  # type: ignore
from src.utils.config import settings  # type: ignore
from src.utils.google_sheet import get_sheet  # type: ignore


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
    return df["BODYWEIGHT_KG"].values[-1]


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
