from abc import ABC
from typing import List, Optional

from pydantic import BaseModel


class StorageData(BaseModel):
    path: str


class UploadData(BaseModel):
    upload_url: str
    fields: dict


class StorageAdapter(ABC):
    def __init__(self) -> None:
        pass

    def create_folder(self, path: str):
        raise NotImplementedError

    def list(self, path: str) -> List[str]:
        raise NotImplementedError

    def upload_url(self, path: str):
        raise NotImplementedError

    def save(self, source_file_path, target_file_path) -> StorageData:
        raise NotImplementedError

    def load(self, source_file_path, target_file_path) -> StorageData:
        raise NotImplementedError
