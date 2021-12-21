from infrastructure.db import DynamodbAdapter
from infrastructure.sqs import SqsTaskAdapter
from ports.db import DbAdapter
from ports.task import TaskAdapter


def get_task_adapater() -> TaskAdapter:
    return SqsTaskAdapter()


def get_db_adapater() -> DbAdapter:
    return DynamodbAdapter()
