"""
Empty specified folder or file.
"""

import sys
from file_convertion_tools.cleanup import cleanup, empty_file  # type: ignore


def main() -> None:
    """Empty specified folder or file.
    """

    path: str = sys.argv[1]
    file_path: str = sys.argv[2]

    cleanup(path)
    empty_file(file_path)


if __name__ == "__main__":
    main()
