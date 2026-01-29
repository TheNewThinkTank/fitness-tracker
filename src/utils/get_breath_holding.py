"""
Get breath holding data from Google Sheet
and plot min, max, and mean duration.
"""

from datetime import datetime as dt  # type: ignore
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.colors as mcolors  # type: ignore
from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
from scipy.stats import linregress  # type: ignore
from src.utils.config import settings  # type: ignore
from src.utils.google_sheet import get_sheet  # type: ignore


def get_sheet_title(year: int, month: int) -> str:
    """Get the title of the Google Sheet.

    :param year: Year
    :type year: int
    :param month: Month
    :type month: int
    :return: Title of the Google Sheet
    :rtype: str
    """

    return f"{year}-{month:02}"


def get_breath_holding(sheet_title: str) -> pd.DataFrame:
    """Get the breath holding data from the Google Sheet.

    :param sheet_title: Title of the Google Sheet
    :type sheet_title: str
    :return: Breath holding data
    :rtype: pd.DataFrame
    """

    sheet = get_sheet(
        sheet_id="1ibiNznk-iWExtRMi0zsbUQL04tXXnpFMKCDfx5rpVt4",
        sheet_title=sheet_title
    )

    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df = df[["DATE", "SET-NUMBER", "DURATION (MM:SS)"]].dropna()

    return df


def make_figure(df, year, sheet_title) -> None:
    """Make a figure of min, max, and mean breath holding duration.

    :param df: Breath holding data
    :type df: pd.DataFrame
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

    plt.plot(summary_df['DATE'], trend_line, color=mcolors.TABLEAU_COLORS['tab:blue'], label='Trend Line')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Date')
    plt.ylabel('Duration (Seconds)')
    plt.title(f'Min, Max, and Mean Breath holding - {sheet_title}')
    plt.legend()
    plt.tight_layout()

    # plt.show()
    plt.savefig(f"{settings['img_path']}{year}/breathholding/{sheet_title}.png")


def main() -> None:
    """Get the breath holding data from the Google Sheet and make a figure.
    """

    today = dt.now().date()
    this_year = today.year
    this_month = today.month

    sheet_title = get_sheet_title(this_year, this_month)
    df = get_breath_holding(sheet_title)
    logger.debug(pformat(df))

    make_figure(df, this_year, sheet_title)


if __name__ == "__main__":
    main()
