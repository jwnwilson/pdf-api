class StorageAdapter:
    def __init__(self) -> None:
        pass

    def save(self, source_file_path, target_file_path):
        raise NotImplementedError

    def load(self, source_file_path, target_file_path):
        raise NotImplementedError
