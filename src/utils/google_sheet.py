"""Google Sheets API.
"""

from __future__ import annotations

from pprint import pformat

import gspread
from google.oauth2.service_account import Credentials
from loguru import logger

from src.utils.config import settings


def get_sheet(sheet_id: str, sheet_title: str) -> gspread.Worksheet:
    """Get a Google Sheet by its ID and title.

    :param sheet_id: ID of the Google Sheet.
    :type sheet_id: str
    :param sheet_title: Title of the Google Sheet.
    :type sheet_title: str
    :return: Google Sheet.
    :rtype: gspread.Worksheet
    """

    if not sheet_id:
        raise ValueError("sheet_id must not be empty.")
    if not sheet_title:
        raise ValueError("sheet_title must not be empty.")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        settings["CREDENTIALS_PATH"],
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet(sheet_title)

    return sheet



def main() -> None:
    """Display a Google Sheet.
    """

    # example: BODYWEIGHT sheet
    sheet_id = "1my1zqAWtkhWXDWsrNf-It_dr541o6C7MndMcHOpKiSs"
    sheet_title = "2023-2024"
    logger.debug(pformat(get_sheet(sheet_id, sheet_title)))


if __name__ == "__main__":
    main()
