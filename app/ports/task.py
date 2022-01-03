from abc import ABC
from typing import Optional

from pydantic import BaseModel


class TaskArgs(BaseModel):
    task_name: str
    params: dict


class TaskData(BaseModel):
    task_id: str
    task_name: str
    params: dict
    status: str


class TaskAdapter(ABC):
    def create_task(self, task_args: TaskArgs) -> TaskData:
        raise NotImplementedError

    def get_task(self) -> TaskData:
        raise NotImplementedError
