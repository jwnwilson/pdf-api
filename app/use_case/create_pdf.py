from domain.pdf import PdfEntity
from ports.db import DbAdapter
from ports.storage import StorageAdapter
from ports.task import TaskData


def create_pdf(
    db_adapter: DbAdapter, storage_adapter: StorageAdapter, task_data: TaskData
) -> TaskData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    # create pdf
    pdf_entity = PdfEntity(db_adapter=db_adapter, storage_adapter=storage_adapter)
    task_data = pdf_entity.create_pdf(task_data)
    return task_data
