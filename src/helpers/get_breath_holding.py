"""_summary_
"""

import datetime
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.colors as mcolors  # type: ignore
from scipy.stats import linregress  # type: ignore

from google_sheet import get_sheet

today = datetime.datetime.now().date()
this_year = today.year
this_month = today.month
sheet_title = f"{this_year}-{this_month:02}"

sheet = get_sheet(
    sheet_id="1ibiNznk-iWExtRMi0zsbUQL04tXXnpFMKCDfx5rpVt4",
    sheet_title=sheet_title
    )


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
