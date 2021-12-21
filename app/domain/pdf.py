import pdfkit
from ports.db import DbAdapter
from ports.pdf import PdfInData
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskData


class PdfEntity:
    def __init__(self, db_adapter: DbAdapter, storage_adapter: StorageAdapter):
        self.db_adapter = db_adapter
        self.storage_adapter = storage_adapter

    def create_pdf(self, pdf_data: TaskData) -> TaskData:
        """[summary]

        Args:
            html (str): [description]
            file_path (str): [description]

        Returns:
            [type]: [description]
        """
        pdf_file_path = "/tmp/pdf_file.pdf"
        # render pdf file
        pdfkit.from_url(pdf_data.kwargs["html_url"], pdf_file_path)

        # save pdf file
        pdf_url = self.storage_adapter.save(pdf_file_path, pdf_file_path)
        pdf_data.result = pdf_url

        # update db record
        self.db_adapter.update(pdf_data.task_id, pdf_data)

        return pdf_data
