import logging
from typing import Any, List

from hex_lib.ports.db import DbAdapter
from hex_lib.ports.task import TaskAdapter, TaskArgs, TaskData
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RegisteredTask(BaseModel):
    name: str
    dependencies: List
    fn: Any


class TaskEntity:
    def __init__(
        self, event_adapter: TaskAdapter, db_adapter: DbAdapter, registered_tasks=None
    ):
        self.event_adapter = event_adapter
        self.db_adapter = db_adapter

    def create_task(self, task_args: TaskArgs) -> TaskData:
        # Create task in event adapter
        task_data: TaskData = self.event_adapter.create_task(task_args)
        # Store task id in db
        logger.info(f"Storing task data in DB: {task_data.task_id}")
        self.db_adapter.create(task_data.dict())
        logger.info(f"Stored task data in DB: {task_data.task_id}")
        return task_data

    def get_task_from_queue(self):
        # Get a task from queue
        task_data: TaskData = self.event_adapter.get_task()
        return task_data

    def get_task_by_id(self, task_id: str) -> TaskData:
        # Get task data from db
        task_data: TaskData = self.db_adapter.read(task_id)
        return task_data
