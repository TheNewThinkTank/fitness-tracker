"""_summary_
"""

import pandas as pd


def get_bw():
    """_summary_

    :return: _description_
    :rtype: _type_
    """

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRPN6RmIAL_8-1x87e48ZkPs2ItSCRp33LxjbeWb7B6WdAZGEX6F_sll70oy58X-abor5xbA2Qt4ZQz/pub?output=csv"

    df = pd.read_csv(url)

    return df["BODYWEIGHT_KG"].values[-1]


if __name__ == "__main__":
    print(get_bw())
