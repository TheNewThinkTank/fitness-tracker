"""
Date: 2021-12-25
Purpose: empty specified folder or file
"""

import sys
from file_convertion_tools.cleanup import cleanup, empty_file  # type: ignore


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
