"""
Flatten nested JSON data into csv format,
e.g. for the great expectations framework to process.
"""

import json
from pathlib import Path
import pandas as pd  # type: ignore


def get_exercise_data(infile: str) -> pd.DataFrame:
    """Read nested JSON file into dataframe.

    :param infile: Filepath to JSON file
    :type infile: str
    :return: Pandas dataframe with flattened JSON data
    :rtype: pd.DataFrame
    """

    with open(infile, "r") as rf:
        json_dict = json.load(rf)

    appended_data = []
    for ex, data in json_dict["exercises"].items():
        df_tmp = pd.json_normalize(data)
        df_tmp["exercise"] = ex
        appended_data.append(df_tmp)

    df = pd.concat(appended_data)

    df["weight"] = df["weight"].apply(lambda x: "'" + str(x) + "'")
    df["date"] = json_dict["date"]
    df["split"] = json_dict["split"]

    return df


def df_to_csv(infile: str, df: pd.DataFrame) -> None:
    """Flatten data, apply additional transformations,
    and write results to csv format.

    :param infile: Filepath to JSON file
    :type infile: str
    :param df: Pandas dataframe with flattened JSON data
    :type df: pd.DataFrame
    """

    col_order = ["date", "split", "exercise", "set_number", "weight", "reps"]
    df = df[col_order]
    df.reset_index(drop=True, inplace=True)

    parts = infile.split("/")
    outfile = f"{parts[0]}/{parts[1]}/CSV/{parts[-1].removesuffix('json')}csv"
    df.to_csv(outfile, index=False)


def main() -> None:
    """Convert all JSON files inside nested folders to CSV.
    """

    dircontent = []
    for path in Path("data/log_archive/JSON/").rglob("*.json"):
        if not any(x in path.stem for x in ("template", "yoga")):
            dircontent.append(path)

    for json_file in dircontent:
        df = get_exercise_data(str(json_file))
        df_to_csv(str(json_file), df)


if __name__ == "__main__":
    main()
