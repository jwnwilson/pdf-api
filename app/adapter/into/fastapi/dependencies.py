import os
from distutils.command import upload

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from hex_lib.adapter.out.db.dynamo import DynamodbAdapter
from hex_lib.adapter.out.queue.sqs import SqsTaskAdapter
from hex_lib.adapter.out.storage.s3 import S3Adapter
from hex_lib.ports.db import DbAdapter
from hex_lib.ports.storage import StorageAdapter
from hex_lib.ports.task import TaskAdapter
from hex_lib.ports.user import UserData
from starlette.requests import Request

ENVIRONMENT = os.environ["ENVIRONMENT"]

security = HTTPBearer()


def get_current_user(
    request: Request, credentials: HTTPBasicCredentials = Depends(security)
) -> UserData:
    # attempt to get user id from authorizer logic
    user_id = request.scope.get("aws", {}).get("context", {}).get("user_id", "1")
    return UserData(user_id=user_id)


def get_task_adapater(user_data: UserData = Depends(get_current_user)) -> TaskAdapter:
    queue_name = f"pdf_task_queue_{ENVIRONMENT}"
    return SqsTaskAdapter({"queue": queue_name}, user=user_data)


def get_db_adapater(user_data: UserData = Depends(get_current_user)) -> DbAdapter:
    table_name = f"pdf_task_{ENVIRONMENT}"
    return DynamodbAdapter(
        config={"table": table_name},
        user=user_data,
        part_key_name="user_id",
        sort_key_name="task_id",
    )


def get_task_storage_adapter(
    user_data: UserData = Depends(get_current_user),
) -> StorageAdapter:
    bucket_name = f"jwnwilson-pdf-task-{ENVIRONMENT}"
    return S3Adapter({"bucket": bucket_name}, user=user_data, upload_prefix="pdf-api")


def get_template_storage_adapter(
    user_data: UserData = Depends(get_current_user),
) -> StorageAdapter:
    bucket_name = f"jwnwilson-pdf-template-{ENVIRONMENT}"
    return S3Adapter({"bucket": bucket_name}, user=user_data, upload_prefix="pdf-api")
