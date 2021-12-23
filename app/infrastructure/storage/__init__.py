import json

import boto3
from ports.storage import StorageAdapter


class S3Adapter(StorageAdapter):
    def upload_url(self):
        pass

    def save(self, source_path: str, target_path: str):
        pass

    def load(self, source_path: str, target_path: str):
        pass
