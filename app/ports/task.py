from abc import ABC
from typing import Optional

from pydantic import BaseModel


class TaskArgs(BaseModel):
    task_name: str
    kwargs: dict


class TaskData(BaseModel):
    task_id: int
    task_name: str
    kwargs: dict
    status: str
    result: Optional[dict]


class TaskAdapter(ABC):
    def create_task(self, task_args: TaskArgs) -> TaskData:
        raise NotImplementedError

    def get_task(self) -> TaskData:
        raise NotImplementedError
