import logging
from typing import List

import boto3
from ports.storage import StorageAdapter, StorageData, UploadUrlData
from ports.user import UserData

logger = logging.getLogger(__name__)


class S3Adapter(StorageAdapter):
    def __init__(self, config: dict, user: UserData) -> None:
        self.bucket_name = config["bucket"]
        self.s3 = boto3.resource("s3")
        self.client = boto3.client("s3")
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.user = user

    def generate_path(self, storage_path: str = ""):
        return f"{self.user.user_id}/{storage_path}".replace("//", "/")

    def get_url(self, key: str) -> str:
        url = f"https://{self.bucket_name}.s3.amazonaws.com/"
        return url + key

    def get_public_url(self, key: str) -> str:
        url: str = self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket_name, "Key": key}
        )
        return url

    def create_folder(self, path):
        path = self.generate_path(path)
        self.client.put_object(Bucket=self.bucket_name, Body="", Key=path)

    def upload_url(self, path: str) -> UploadUrlData:
        path = self.generate_path(path)
        upload_data = self.client.generate_presigned_post(self.bucket_name, path)
        return UploadUrlData(
            upload_url=upload_data["url"], fields=upload_data["fields"]
        )

    def list(
        self, path: str, include_files=True, include_folders=True, as_urls=False
    ) -> List[str]:
        prefix = self.generate_path(path)
        objs = self.client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix, Delimiter="/"
        )
        results: List[str] = []
        if include_files:
            results = results + [obj["Key"] for obj in objs.get("Contents", [])]
        if include_folders:
            results = results + [
                obj["Prefix"] for obj in objs.get("CommonPrefixes", [])
            ]
        if as_urls:
            results = [self.get_url(r) for r in results]
        return sorted(results)

    def save(self, source_path: str, target_path: str) -> StorageData:
        target_path = self.generate_path(target_path)
        logger.info(
            f"Saving file: {source_path} to s3 bucket: {self.bucket_name}, key: {target_path}"
        )
        self.bucket.upload_file(source_path, target_path)
        return StorageData(path=self.get_url(target_path))

    def load(self, source_path: str, target_path: str):
        pass
