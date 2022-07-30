from domain.task import TaskEntity
from hex_lib.ports.db import DbAdapter
from hex_lib.ports.task import TaskAdapter, TaskArgs, TaskData


def generate_pdf_task(
    event_adapter: TaskAdapter,
    db_adapter: DbAdapter,
    pdf_task_data: TaskArgs,
) -> TaskData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    # create pdf task
    task_service = TaskEntity(event_adapter=event_adapter, db_adapter=db_adapter)
    pdf_task_data = task_service.create_task(pdf_task_data)

    # return pdf task data
    return pdf_task_data
