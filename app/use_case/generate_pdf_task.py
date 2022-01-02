from domain.task import TaskEntity
from ports.db import DbAdapter
from ports.pdf import PdfGenerateData
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskArgs, TaskData


def generate_pdf_task(
    event_adapter: TaskAdapter,
    db_adapter: DbAdapter,
    pdf_data: PdfGenerateData,
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
    task_args = TaskArgs(task_name="create_pdf", kwargs=pdf_data.dict())
    pdf_task_data = task_service.create_task(task_args)

    # return pdf task data
    return pdf_task_data
