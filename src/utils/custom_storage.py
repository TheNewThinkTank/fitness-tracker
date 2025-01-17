"""Extend TinyDB to use YAML as storage.
"""

import yaml  # type: ignore
from tinydb import TinyDB  # type: ignore
from tinydb.storages import Storage, touch  # type: ignore
from src.utils.config_loader import ConfigLoader  # type: ignore


class YAMLStorage(Storage):
    """YAML storage for TinyDB.
    """
    def __init__(self, filename, **kwargs):
        super().__init__()
        touch(filename, create_dirs=True)  # Create file if not exists
        self.kwargs = kwargs
        self._handle = open(filename, 'r+')
        self.filename = filename

    def read(self):
        with open(self.filename) as handle:
            try:
                data = yaml.safe_load(handle.read())
                return data
            except yaml.YAMLError:
                return None

    def write(self, data):
        with open(self.filename, 'w+') as handle:
            yaml.dump(data, handle, sort_keys=False)

    def close(self):
        self._handle.close()


def main() -> None:
    """Load a TinyDB database using YAML storage.
    """

    env_vars = ConfigLoader.load_env_variables()
    config = ConfigLoader.load_config()

    in_file_name = "/db.yml"

    test_path = f'{config["google_drive_data_path"]}/{env_vars["athlete"]}{in_file_name}'

    db = TinyDB(test_path, storage=YAMLStorage)
    print(db)


if __name__ == "__main__":
    main()
