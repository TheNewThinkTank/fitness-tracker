"""
Date: 2022-02-21
Author: Gustav Collin Rasmussen
Purpose: flatten nested JSON data into csv format,
  for the great expectations framework to process.
"""

import json
import pandas as pd


def json2csv(infile) -> None:
    """Read nested JSON file, flatten it, apply additional transformations,
    and write results to csv format"""

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
    col_order = ["date", "split", "exercise", "set no.", "weight", "reps"]
    df = df[col_order]
    df.reset_index(drop=True, inplace=True)

    parts = infile.split("/")
    outfile = f"{parts[0]}/{parts[1]}/CSV/{parts[-1].removesuffix('json')}csv"
    df.to_csv(outfile, index=False)


def main():
    from pathlib import Path

    dircontent = []
    for path in Path("data/log_archive/JSON/").rglob("*.json"):
        if not any(x in path.stem for x in ("template", "yoga")):
            dircontent.append(path)

    for json_file in dircontent:
        json2csv(str(json_file))


if __name__ == "__main__":
    main()
