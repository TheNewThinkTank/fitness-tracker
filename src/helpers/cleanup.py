"""
Date: 2021-12-25
Author: Gustav Collin Rasmussen
Purpose: empty specified folder
"""

import os
import pathlib
import sys


def cleanup(path) -> None:
    """Empty all files in path."""
    p = pathlib.Path(path)
    all_files = os.listdir(p)
    for f in all_files:
        os.remove(p / f)


def empty_file(file_path) -> None:
    """Empty content in file."""
    open(file_path, "w").close()


def main(path, file_path):
    cleanup(path)
    empty_file(file_path)


if __name__ == "__main__":
    path = sys.argv[1]
    file_path = sys.argv[2]
    main(path, file_path)
