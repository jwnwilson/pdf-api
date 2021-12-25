from infrastructure.db import DynamodbAdapter
from infrastructure.sqs import SqsTaskAdapter
from infrastructure.storage import S3Adapter
from ports.db import DbAdapter
from ports.task import TaskAdapter
from ports.storage import StorageAdapter


def get_task_adapater() -> TaskAdapter:
    queue_name = "pdf_task_queue"
    return SqsTaskAdapter({
        "queue": queue_name
    })


def get_db_adapater() -> DbAdapter:
    table_name = "pdf_generation"
    return DynamodbAdapter(config={
        "table_name": table_name
    })


def get_storage_adapater() -> StorageAdapter:
    bucket_name = "pdf_file_storage"
    return S3Adapter({
        "bucket": bucket_name
    })