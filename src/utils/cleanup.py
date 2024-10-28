"""
Date: 2021-12-25
Purpose: empty specified folder or file
"""

import os
import pathlib
import sys


def cleanup(path: str) -> None:
    """Empty all files in path.

    :param path: _description_
    :type path: str
    """
    p = pathlib.Path(path)
    all_files = os.listdir(p)
    for f in all_files:
        os.remove(p / f)


def empty_file(file_path: str) -> None:
    """Empty content in file.

    :param file_path: _description_
    :type file_path: str
    """
    open(file_path, "w").close()


def main() -> None:
    """_summary_

    :param path: _description_
    :type path: str
    :param file_path: _description_
    :type file_path: str
    """

    path: str = sys.argv[1]
    file_path: str = sys.argv[2]

    cleanup(path)
    empty_file(file_path)


if __name__ == "__main__":
    main()
