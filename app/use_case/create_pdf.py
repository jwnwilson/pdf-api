from hex_lib.ports.db import DbAdapter
from hex_lib.ports.storage import StorageAdapter

from domain.pdf import PdfCreateOutData, PdfTemplateEntity
from ports.pdf import PdfCreateInData


def upload_static(
    db_adapter: DbAdapter,
    task_storage_adapter: StorageAdapter,
    template_storage_adapter: StorageAdapter,
    pdf_data: PdfCreateInData,
) -> PdfCreateOutData:
    pdf_entity = PdfTemplateEntity(
        db_adapter=db_adapter,
        template_storage_adapter=template_storage_adapter,
        task_storage_adapter=task_storage_adapter,
    )
    task_data: PdfCreateOutData = pdf_entity.upload_static(pdf_data)
    return task_data


def create_pdf(
    db_adapter: DbAdapter,
    task_storage_adapter: StorageAdapter,
    template_storage_adapter: StorageAdapter,
    pdf_data: PdfCreateInData,
) -> PdfCreateOutData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    pdf_entity = PdfTemplateEntity(
        db_adapter=db_adapter,
        template_storage_adapter=template_storage_adapter,
        task_storage_adapter=task_storage_adapter,
    )
    task_data: PdfCreateOutData = pdf_entity.create_pdf_template(pdf_data)
    return task_data
