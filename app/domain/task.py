from typing import Any, List

from ports.db import DbAdapter
from ports.task import TaskAdapter, TaskArgs, TaskData
from pydantic import BaseModel


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
        print("task_data.dict()", task_data.dict())
        self.db_adapter.create(task_data.dict())
        return task_data

    def get_task_from_queue(self):
        # Get a task from queue
        task_data: TaskData = self.event_adapter.get_task()
        return task_data

    def get_task_by_id(self, task_id: str) -> TaskData:
        # Get task data from db
        task_data: TaskData = self.db_adapter.read(task_id)
        return task_data
