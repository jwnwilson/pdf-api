import json
from typing import List
import boto3
from ports.storage import StorageAdapter


class S3Adapter(StorageAdapter):
    def __init__(self, config: dict) -> None:
        self.bucket_name = config["bucket"]
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self.bucket_name)

    def upload_url(self):
        pass

    def list(self, path:str) -> List[str]:
        url = f'https://{self.bucket_name}.s3.amazonaws.com/'
        return [url + obj.key for obj in self.bucket.objects.filter(Prefix=path)]

    def save(self, source_path: str, target_path: str):
        pass

    def load(self, source_path: str, target_path: str):
        pass
