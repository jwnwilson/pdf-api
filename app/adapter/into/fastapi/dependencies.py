import os

from infrastructure.db import DynamodbAdapter
from infrastructure.sqs import SqsTaskAdapter
from infrastructure.storage import S3Adapter
from ports.db import DbAdapter
from ports.storage import StorageAdapter
from ports.task import TaskAdapter

ENVIRONMENT = os.environ["ENVIRONMENT"]


def get_task_adapater() -> TaskAdapter:
    queue_name = f"pdf_task_queue_{ENVIRONMENT}"
    return SqsTaskAdapter({"queue": queue_name})


def get_db_adapater() -> DbAdapter:
    table_name = f"pdf_task_{ENVIRONMENT}"
    return DynamodbAdapter(config={"table": table_name})


def get_storage_adapater() -> StorageAdapter:
    bucket_name = f"jwnwilson-pdf-task-{ENVIRONMENT}"
    return S3Adapter({"bucket": bucket_name})


def get_template_storage_adapater() -> StorageAdapter:
    bucket_name = f"jwnwilson-pdf-template-{ENVIRONMENT}"
    return S3Adapter({"bucket": bucket_name})
