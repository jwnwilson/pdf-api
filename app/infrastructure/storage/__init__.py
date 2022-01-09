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

        self.url_prefix = f"https://{self.bucket_name}.s3.amazonaws.com/"
        self.upload_user_access_id = "/pdf-api/upload_access_id"
        self.upload_user_secret_key = "/pdf-api/upload_secret_key"

    def _get_upload_client(self):
        client = boto3.client("ssm")
        access_id = client.get_parameter(
            Name=self.upload_user_access_id, WithDecryption=True
        )
        secret_key = client.get_parameter(
            Name=self.upload_user_secret_key, WithDecryption=True
        )
        s3_client = boto3.client('s3',
            aws_access_key_id=access_id,
            aws_secret_access_key=secret_key,
        )

        return s3_client

    def generate_key(self, storage_path: str = ""):
        return f"{self.user.user_id}/{storage_path}".replace("//", "/")

    def get_url(self, key: str) -> str:
        return self.url_prefix + key

    def get_key(self, url: str) -> str:
        key = url.replace(self.url_prefix, "")
        return key

    def get_public_url(self, storage_path: str) -> str:
        key = self.generate_key(storage_path)
        public_url: str = self._get_upload_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key, "Expires": 3600},
        )
        return public_url

    def create_folder(self, path):
        path = self.generate_key(path)
        self.client.put_object(Bucket=self.bucket_name, Body="", Key=path)

    def upload_url(self, path: str) -> UploadUrlData:
        path = self.generate_key(path)
        upload_data = self._get_upload_client().generate_presigned_post(
            Bucket=self.bucket_name, Key=path, ExpiresIn=3600
        )
        return UploadUrlData(
            upload_url=upload_data["url"], fields=upload_data["fields"]
        )

    def list(
        self, path: str, include_files=True, include_folders=True, as_urls=False
    ) -> List[str]:
        prefix = self.generate_key(path)
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
        target_path = self.generate_key(target_path)
        logger.info(
            f"Saving file: {source_path} to s3 bucket: {self.bucket_name}, key: {target_path}"
        )
        self.bucket.upload_file(source_path, target_path)
        return StorageData(path=self.get_url(target_path))

    def load(self, source_path: str, target_path: str):
        pass
