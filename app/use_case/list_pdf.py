from typing import List

from hex_lib.ports.db import DbAdapter
from hex_lib.ports.storage import StorageAdapter

from domain.pdf import PdfTemplateEntity


def list_pdf(
    db_adapter: DbAdapter,
    task_storage_adapter: StorageAdapter,
    template_storage_adapter: StorageAdapter,
) -> List[str]:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    # create pdf
    pdf_entity = PdfTemplateEntity(
        db_adapter=db_adapter,
        task_storage_adapter=task_storage_adapter,
        template_storage_adapter=template_storage_adapter,
    )
    task_data: List[str] = pdf_entity.list_pdf_templates()
    return task_data
