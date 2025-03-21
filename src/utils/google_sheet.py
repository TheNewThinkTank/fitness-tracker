"""Google Sheets API.
"""

# TODO: Move to key-master repo, publish to PyPI.
from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
import gspread
from google.oauth2.service_account import Credentials


def get_sheet(sheet_id: str, sheet_title: str) -> gspread.Worksheet:
    """Get a Google Sheet by its ID and title.

    :param sheet_id: ID of the Google Sheet.
    :type sheet_id: str
    :param sheet_title: Title of the Google Sheet.
    :type sheet_title: str
    :return: Google Sheet.
    :rtype: gspread.Worksheet
    """

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        "local_assets/credentials.json",
        scopes=scopes
        )
    client = gspread.authorize(creds)
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet(sheet_title)

    return sheet


def update_sheet() -> None:
    """Update a Google Sheet.
    """
    # worksheet = sh.get_worksheet(0)
    # worksheet = sh.worksheet(sheet_title)

    # sheets = workbook.worksheets()
    # logger.debug(pformat(sheets))

    # values = [
    #     ["Name", "Price", "Quantity"],
    #     ["Basketball", 29.99, 1],
    #     ["Jeans", 39.99, 4],
    #     ["Soap", 7.99, 3],
    # ]

    # sheets = map(lambda x: x.title, workbook.worksheets())
    # logger.debug(pformat(list(sheets)))

    # sheet.update_title("August 2024")
    # sheet.update_cell(1, 1, "new value")

    # value = sheet.acell("A1").value
    # value = sheet.cell(1, 1).value
    # logger.debug(pformat(value))

    # cell = sheet.find("2024-08-03")
    # logger.debug(pformat(cell.row, cell.col))

    # new_worksheet_name = "Values"

    # if new_worksheet_name in sheets:
    #     sheet = workbook.worksheet(new_worksheet_name)
    # else:
    #     sheet = workbook.add_worksheet(new_worksheet_name, rows=10, cols=10)

    # sheet.clear()
    # sheet.update(f"A1:C{len(values)}", values)
    # sheet.update_cell(len(values) + 1, 2, "=sum(B2:B4)")
    # sheet.update_cell(len(values) + 1, 3, "=sum(C2:C4)")
    # sheet.format("A1:C1", {"textFormat": {"bold": True}})
    return


def main() -> None:
    """Display a Google Sheet.
    """

    # example: BODYWEIGHT sheet
    sheet_id = "1my1zqAWtkhWXDWsrNf-It_dr541o6C7MndMcHOpKiSs"
    sheet_title = "2023-2024"
    logger.debug(pformat(get_sheet(sheet_id, sheet_title)))


if __name__ == "__main__":
    main()
