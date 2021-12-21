from domain.task import TaskEntity
from ports.db import DbAdapter
from ports.pdf import PdfInData
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskArgs, TaskData


def create_pdf(
    event_adapter: TaskAdapter,
    db_adapter: DbAdapter,
    storage_adapter: StorageAdapter,
    pdf_data: PdfInData,
) -> TaskData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    # store html data to create pdf later
    html_file = pdf_data.html_url.split("/")[-1]
    html_url = storage_adapter.save(pdf_data.html_url, html_file)

    # create pdf task
    task_service = TaskEntity(event_adapter=event_adapter, db_adapter=db_adapter)
    task_args = TaskArgs(task_name="create_pdf", kwargs={"html_url": html_url})
    pdf_task_data = task_service.create_task(task_args)

    # return pdf task data
    return pdf_task_data
