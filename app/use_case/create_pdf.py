from domain.pdf import PdfTemplateEntity, PdfCreateOutData
from ports.db import DbAdapter
from ports.pdf import PdfCreateInData
from ports.storage import StorageAdapter


def create_pdf(
    db_adapter: DbAdapter, storage_adapter: StorageAdapter, pdf_data: PdfCreateInData
) -> PdfCreateOutData:
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    # create pdf
    pdf_entity = PdfTemplateEntity(
        db_adapter=db_adapter, template_storage_adapter=storage_adapter
    )
    task_data: PdfCreateOutData = pdf_entity.create_pdf_template(pdf_data)
    return task_data
