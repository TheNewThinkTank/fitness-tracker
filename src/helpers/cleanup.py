"""
Date: 2021-12-25
Author: Gustav Collin Rasmussen
Purpose: empty specified folder
"""

import os
import pathlib


def cleanup(path) -> None:
    """Empty all files in path."""

    p = pathlib.Path(path)
    all_files = os.listdir(p)

    for f in all_files:
        os.remove(p / f)

    assert os.listdir(p) == []

    return
