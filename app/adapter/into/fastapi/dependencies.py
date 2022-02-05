import os

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from infrastructure.db import DynamodbAdapter
from infrastructure.sqs import SqsTaskAdapter
from infrastructure.storage import S3Adapter
from ports.db import DbAdapter
from ports.storage import StorageAdapter
from ports.task import TaskAdapter
from ports.user import UserData
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
    return DynamodbAdapter(config={"table": table_name}, user=user_data)


def get_task_storage_adapater(
    user_data: UserData = Depends(get_current_user),
) -> StorageAdapter:
    bucket_name = f"jwnwilson-pdf-task-{ENVIRONMENT}"
    return S3Adapter({"bucket": bucket_name}, user=user_data)


def get_template_storage_adapater(
    user_data: UserData = Depends(get_current_user),
) -> StorageAdapter:
    bucket_name = f"jwnwilson-pdf-template-{ENVIRONMENT}"
    return S3Adapter({"bucket": bucket_name}, user=user_data)
