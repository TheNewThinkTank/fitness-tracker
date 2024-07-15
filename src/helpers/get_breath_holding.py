"""_summary_
"""

import datetime
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore


def get_breath_holding():
    """_summary_

    :return: _description_
    :rtype: _type_
    """

    base_url = "https://docs.google.com/spreadsheets"
    url = base_url + "/d/e/2PACX-1vRqzqJPhFMBBrMw3710Q1Ws2eUTqVDUTpNdXqxneW2otr_4xfgVYWLxrIH8NDJOeBbs8Pq4ZLs76eEi/pub?output=csv"

    df = pd.read_csv(url)

    cols = [
        "DATE",
        "SET-NUMBER",
        "START-TIME (HH:MM)",
        "DURATION (MM:SS)",
        "FROM-INHALE",
        "CONTROLLED-HYPERVENTILATION",
        "TIMEZONE",
        "LOCATION",
        "NOTES",
    ]

    return df[["DATE", "SET-NUMBER", "DURATION (MM:SS)"]].dropna()  # df[""].values[-1]


def make_figure(df):
    print(df)

    today = datetime.datetime.now().date()

    # Convert 'DURATION (HH:MM)' to seconds
    df['DURATION (MM:SS)'] = df['DURATION (MM:SS)'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    # Rename column for clarity
    df = df.rename(columns={'DURATION (MM:SS)': 'DURATION (Seconds)'})

    # Compute min, max, and mean duration for each date
    summary_df = df.groupby('DATE')['DURATION (Seconds)'].agg(['min', 'max', 'mean']).reset_index()

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

    # Add labels and title
    plt.xlabel('Set Number')
    plt.ylabel('Duration (Seconds)')
    plt.title('Min, Max, and Mean Breath holding')

    # Show plot
    # plt.show()
    plt.savefig(f"docs/project_docs/img/breathholding/{today}.png")


if __name__ == "__main__":
    make_figure(get_breath_holding())
