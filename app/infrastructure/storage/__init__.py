import logging
from typing import List

import boto3
from ports.storage import StorageAdapter

from app.ports.storage import StorageData

logger = logging.getLogger(__name__)


class S3Adapter(StorageAdapter):
    def __init__(self, config: dict) -> None:
        self.bucket_name = config["bucket"]
        self.s3 = boto3.resource("s3")
        self.client = boto3.client("s3")
        self.bucket = self.s3.Bucket(self.bucket_name)

    def _get_url(self, key: str) -> str:
        url = f"https://{self.bucket_name}.s3.amazonaws.com/"
        return url + key

    def create_folder(self, path):
        key = self.bucket.new_key(path)
        key.set_contents_from_string("")

    def upload_url(self):
        pass

    def list(self, path: str, folders=False) -> List[str]:
        if folders:
            objs = self.client.list_objects_v2(Bucket=self.bucket_name, Delimiter=path)
            return [obj["Prefix"] for obj in objs["CommonPrefixes"]]
        else:
            print("The fuck?")
            print("path", path)
            return [
                self._get_url(obj.key)
                for obj in self.bucket.objects.filter(Prefix=path)
            ]

    def save(self, source_path: str, target_path: str) -> StorageData:
        logger.info(
            f"Saving file: {source_path} to s3 bucket: {self.bucket_name}, key: {target_path}"
        )
        self.bucket.upload_file(source_path, target_path)
        return StorageData(path=self._get_url(target_path))

    def load(self, source_path: str, target_path: str):
        pass
