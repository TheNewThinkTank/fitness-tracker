"""Get the bodyweight from the google sheet.
"""

import pandas as pd  # type: ignore
from google_sheet import get_sheet  # type: ignore


def get_bw() -> float:
    """Get the bodyweight from the google sheet.

    :return: Bodyweight in kg
    :rtype: float
    """

    URL = (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vRPN6RmIAL_8-1x87e48ZkPs2"
        "ItSCRp33LxjbeWb7B6WdAZGEX6F_sll70oy58X-abor5xbA2Qt4ZQz/"
        "pub?output=csv"
    )
    df = pd.read_csv(URL)

    return df["BODYWEIGHT_KG"].values[-1]


def main() -> None:
    """Get the bodyweight from the google sheet.
    """
    sheet = get_sheet(
    sheet_id="1my1zqAWtkhWXDWsrNf-It_dr541o6C7MndMcHOpKiSs",
    sheet_title="2023-2024"
    )
    print(sheet)
    print(get_bw())


if __name__ == "__main__":
    main()
