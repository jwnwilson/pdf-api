from abc import ABC

from pydantic import BaseModel

class StorageData(BaseModel):
    path: str
    upload_url: str


class StorageAdapter(ABC):
    def __init__(self) -> None:
        pass

    def upload_url(self) -> StorageData:
        raise NotImplementedError

    def save(self, source_file_path, target_file_path) -> StorageData:
        raise NotImplementedError

    def load(self, source_file_path, target_file_path) -> StorageData:
        raise NotImplementedError
