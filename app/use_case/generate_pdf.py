from domain.pdf import PdfEntity
from ports.db import DbAdapter
from ports.pdf import PdfData
from ports.storage import StorageAdapter


def generate_pdf(
    db_adapter: DbAdapter, storage_adapter: StorageAdapter, pdf_data: PdfData
):
    """[summary]

    Args:
        html (str): [description]
        file_path (str): [description]

    Returns:
        [type]: [description]
    """
    # create pdf
    pdf_entity = PdfEntity(db_adapter=db_adapter, storage_adapter=storage_adapter)
    task_data = pdf_entity.generate_pdf(PdfData)
    return task_data
