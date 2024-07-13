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

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzqJPhFMBBrMw3710Q1Ws2eUTqVDUTpNdXqxneW2otr_4xfgVYWLxrIH8NDJOeBbs8Pq4ZLs76eEi/pub?output=csv"
    df = pd.read_csv(url)

    cols = [
        "DATE",
        "SET-NUMBER",
        "START-TIME (HH:MM)",
        "TIMEZONE",
        "DURATION (HH:MM)",
        "FROM-INHALE",
        "CONTROLLED-HYPERVENTILATION",
        "NOTES",
    ]

    return df[["DATE", "SET-NUMBER", "DURATION (HH:MM)"]].dropna()  # df[""].values[-1]


def main():
    df = get_breath_holding()

    # Convert 'DURATION (HH:MM)' to seconds
    df['DURATION (HH:MM)'] = df['DURATION (HH:MM)'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    # Rename column for clarity
    df = df.rename(columns={'DURATION (HH:MM)': 'DURATION (Seconds)'})

    # Create Seaborn barplot
    plt.figure(figsize=(10, 6))
    sns.barplot(x='SET-NUMBER', y='DURATION (Seconds)', data=df)

    # Add labels and title
    plt.xlabel('Set Number')
    plt.ylabel('Duration (Seconds)')
    plt.title('Breath holding 2024-07-13')

    # Show plot
    # plt.show()
    plt.savefig("docs/project_docs/img/breathholding/2024-07-13.png")


if __name__ == "__main__":
    main()
