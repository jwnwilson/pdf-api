from abc import ABC

from pydantic import BaseModel


class TaskArgs(BaseModel):
    task_name: str
    args: list
    kwargs: dict


class TaskData(BaseModel):
    task_id: int
    task_name: str
    args: list
    kwargs: dict
    status: str
    result: dict


class TaskAdapter(ABC):
    def create_task(self, task_name: str, task_args: TaskArgs) -> TaskData:
        raise NotImplementedError

    def get_task(self) -> TaskData:
        raise NotImplementedError
