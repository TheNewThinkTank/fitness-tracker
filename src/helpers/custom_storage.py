import yaml  # type: ignore

from tinydb import TinyDB  # type: ignore
from tinydb.storages import Storage, touch  # type: ignore


class YAMLStorage(Storage):
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


if __name__ == "__main__":
    test_path = "/Users/gustavcollinrasmussen/Google Drive/My Drive/DATA/fitness-tracker-data/gustav_rasmussen/db.yml"
    db = TinyDB(test_path, storage=YAMLStorage)
