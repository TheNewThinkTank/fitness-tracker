"""_summary_
"""

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


def main():
    df = get_breath_holding()

    # Convert 'DURATION (HH:MM)' to seconds
    df['DURATION (MM:SS)'] = df['DURATION (MM:SS)'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    # Rename column for clarity
    df = df.rename(columns={'DURATION (MM:SS)': 'DURATION (Seconds)'})

    # Create Seaborn barplot
    plt.figure(figsize=(12, 6))
    # sns.barplot(x='SET-NUMBER', y='DURATION (Seconds)', data=df)
    sns.barplot(x='SET-NUMBER', y='DURATION (Seconds)', hue='DATE', data=df)

    # Add labels and title
    plt.xlabel('Set Number')
    plt.ylabel('Duration (Seconds)')
    plt.title('Breath holding')

    # Show plot
    # plt.show()
    plt.savefig("docs/project_docs/img/breathholding/2024-07-14.png")


if __name__ == "__main__":
    main()
