import pdfkit
from ports.db import DbAdapter
from ports.pdf import PdfData, PdfGenerateData
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskData


class PdfEntity:
    def __init__(self, db_adapter: DbAdapter, storage_adapter: StorageAdapter):
        self.db_adapter = db_adapter
        self.storage_adapter = storage_adapter

    def create_pdf(self, pdf_data: PdfData) -> PdfGenerateData:
        """[summary]

        Args:
            pdf_data (PdfData): [description]

        Returns:
            PdfGenerateData: [description]
        """
        # Download html and save in storage
        # Download images and save in storage
        # Return pdf data

    def get_pdf(self, uuid: str) -> PdfData:
        # Get image files from storage
        files = self.storage_adapter.list(uuid)
        html_path = files.filter(lambda x: x.endswith("html"))[0]
        image_urls = files.filter(lambda x: not x.endswith("html"))

        return PdfData(
            pdf_uuid=uuid,
            html_path=html_path,
            image_urls=image_urls
        )

    def generate_pdf(self, pdf_gen_data: PdfGenerateData) -> PdfGenerateData:
        """[summary]

        Args:
            html (str): [description]
            file_path (str): [description]

        Returns:
            [type]: [description]
        """
        pdf_file_path = f"{pdf_gen_data.pdf_uuid}/pdf.html"
        local_pdf_file_path = f"/tmp/{pdf_file_path}"
        # get pdf data from uuid
        pdf_data = self.get_pdf(pdf_gen_data.pdf_uuid)
        
        # render pdf file
        pdfkit.from_url(pdf_data.kwargs["html_url"], local_pdf_file_path)

        # save pdf file
        pdf_url = self.storage_adapter.save(pdf_file_path, pdf_file_path)
        pdf_data.result = pdf_url
        pdf_data.status = "Complete"

        # update db record
        self.db_adapter.update(pdf_data.task_id, pdf_data)

        return pdf_data
