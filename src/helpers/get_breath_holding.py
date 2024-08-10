"""_summary_
"""

import datetime
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.colors as mcolors  # type: ignore
from scipy.stats import linregress  # type: ignore

import gspread
from google.oauth2.service_account import Credentials

today = datetime.datetime.now().date()
this_year = today.year
this_month = today.month
sheet_title = f"{this_year}-{this_month:02}"

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    "local_assets/credentials.json",
    scopes=scopes
    )
client = gspread.authorize(creds)

sheet_id = "1ibiNznk-iWExtRMi0zsbUQL04tXXnpFMKCDfx5rpVt4"
workbook = client.open_by_key(sheet_id)

# worksheet = sh.get_worksheet(0)
# worksheet = sh.worksheet(sheet_title)
sheet = workbook.worksheet(sheet_title)

# sheets = workbook.worksheets()
# print(sheets)

# values = [
#     ["Name", "Price", "Quantity"],
#     ["Basketball", 29.99, 1],
#     ["Jeans", 39.99, 4],
#     ["Soap", 7.99, 3],
# ]

# sheets = map(lambda x: x.title, workbook.worksheets())
# print(list(sheets))

# sheet.update_title("August 2024")
# sheet.update_cell(1, 1, "new value")

# value = sheet.acell("A1").value
# value = sheet.cell(1, 1).value
# print(value)

# cell = sheet.find("2024-08-03")
# print(cell.row, cell.col)

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


def get_breath_holding():
    """_summary_

    :return: _description_
    :rtype: _type_
    """

    # base_url = "https://docs.google.com/spreadsheets"
    # url = base_url + "/d/e/2PACX-1vRqzqJPhFMBBrMw3710Q1Ws2eUTqVDUTpNdXqxneW2otr_4xfgVYWLxrIH8NDJOeBbs8Pq4ZLs76eEi/pub?output=csv"

    data = sheet.get_all_records()
    df = pd.DataFrame(data)  # pd.read_csv(url)
    df = df[["DATE", "SET-NUMBER", "DURATION (MM:SS)"]].dropna()

    # cols = [
    #     "DATE",
    #     "SET-NUMBER",
    #     "START-TIME (HH:MM)",
    #     "DURATION (MM:SS)",
    #     "FROM-INHALE",
    #     "CONTROLLED-HYPERVENTILATION",
    #     "TIMEZONE",
    #     "LOCATION",
    #     "NOTES",
    # ]

    return df


def make_figure(df):
    """_summary_

    :param df: _description_
    :type df: _type_
    """

    # Convert 'DURATION (HH:MM)' to seconds
    df['DURATION (MM:SS)'] = df['DURATION (MM:SS)'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])
        )

    # Rename column for clarity
    df = df.rename(columns={'DURATION (MM:SS)': 'DURATION (Seconds)'})

    # Compute min, max, and mean duration for each date
    summary_df = df.groupby('DATE')['DURATION (Seconds)'].agg(
        ['min', 'max', 'mean']
        ).reset_index()

    # Convert dates to ordinal for regression
    summary_df['DATE_ORD'] = pd.to_datetime(summary_df['DATE']).map(pd.Timestamp.toordinal)

    plt.figure(figsize=(12, 6))
    sns.barplot(x='DATE', y='mean', data=summary_df, color='skyblue', capsize=0.2)
    plt.errorbar(
        x=summary_df['DATE'],
        y=summary_df['mean'],
        yerr=[summary_df['mean'] - summary_df['min'],
              summary_df['max'] - summary_df['mean']],
              fmt='none',
              c='black'
        )

    # Linear regression for trend line
    slope, intercept, r_value, p_value, std_err = linregress(
        summary_df['DATE_ORD'], summary_df['mean']
        )
    trend_line = intercept + slope * summary_df['DATE_ORD']

    # Plot trend line
    plt.plot(summary_df['DATE'], trend_line, color=mcolors.TABLEAU_COLORS['tab:blue'], label='Trend Line')

    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')

    plt.xlabel('Date')
    plt.ylabel('Duration (Seconds)')
    plt.title(f'Min, Max, and Mean Breath holding - {sheet_title}')

    plt.legend()
    plt.tight_layout()

    # plt.show()
    plt.savefig(f"docs/project_docs/img/breathholding/{sheet_title}.png")


if __name__ == "__main__":
    # print(get_breath_holding())
    make_figure(get_breath_holding())
