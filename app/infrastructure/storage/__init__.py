import logging
from typing import List

import boto3
from ports.storage import StorageAdapter, UploadData

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
        if not path.endswith("/"):
            path = path + "/"
        self.client.put_object(Bucket=self.bucket_name, Body="", Key=path)

    def upload_url(self, path: str) -> UploadData:
        upload_data = self.client.generate_presigned_post(self.bucket_name, path)
        return UploadData(upload_url=upload_data["url"], fields=upload_data["fields"])

    def list(self, path: str) -> List[str]:
        objs = self.client.list_objects_v2(Bucket=self.bucket_name, Delimiter=path)
        files = [obj["Key"] for obj in objs.get("Contents", [])]
        folders = [obj["Prefix"] for obj in objs.get("CommonPrefixes", [])]

        return sorted(files + folders)

    def save(self, source_path: str, target_path: str) -> StorageData:
        logger.info(
            f"Saving file: {source_path} to s3 bucket: {self.bucket_name}, key: {target_path}"
        )
        self.bucket.upload_file(source_path, target_path)
        return StorageData(path=self._get_url(target_path))

    def load(self, source_path: str, target_path: str):
        pass
