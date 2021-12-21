from domain.task import TaskEntity
from ports.db import DbAdapter
from ports.task import TaskAdapter, TaskData


def get_pdf(event_adapter: TaskAdapter, db_adapter: DbAdapter, pdf_id: str) -> TaskData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    task_service = TaskEntity(event_adapter=event_adapter, db_adapter=db_adapter)
    # return pdf task data
    return task_service.get_task_by_id(pdf_id)
