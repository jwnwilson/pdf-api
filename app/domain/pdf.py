import pdfkit
import requests
import uuid
import re

from ports.db import DbAdapter
from ports.pdf import PdfData, PdfGenerateData
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskData


class PdfEntity:
    def __init__(self, db_adapter: DbAdapter, storage_adapter: StorageAdapter):
        self.db_adapter = db_adapter
        self.storage_adapter = storage_adapter

    def _get_file_name(self, url, response) -> str:
        fname = ''
        if "Content-Disposition" in response.headers.keys():
            fname = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
        else:
            fname = url.split("/")[-1]
            
        return fname

    def _save_url_to_file(self, pdf_id, url, file_name=None) -> str:
        # Download file
        file_response = requests.get(url)
        # Get file name from url file name or use url path
        if not file_name:
            file_name = self._get_file_name(url, file_response)
        file_path = f"{pdf_id}/{file_name}.html"
        local_html_path = "/tmp/" + file_path
        
        with open(local_html_path, "w") as file:
            file.write(file_response.text)
        
        # Save in our storage adapter
        self.storage_adapter.save(local_html_path, file_path)

        return file_path


    def create_pdf(self, pdf_data: PdfData) -> PdfGenerateData:
        """[summary]

        Args:
            pdf_data (PdfData): [description]

        Returns:
            PdfGenerateData: [description]
        """
        pdf_id = uuid.uuid4()

        # Download html and save in storage
        html_path = self._save_url_to_file(pdf_id, pdf_data.html_url, file_name="template.html")

        # Download images and save in storage
        image_urls = []
        for image_url in pdf_data.images_urls:
            image_urls.append(
                self._save_url_to_file(pdf_id, image_url)
            )

        # Return pdf data
        return PdfGenerateData(
            pdf_id=pdf_id
        )

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
        # get pdf data from uuid
        pdf_data = self.get_pdf(pdf_gen_data.pdf_uuid)
        
        # render pdf file
        pdf_file_path = f"{pdf_gen_data.pdf_uuid}/render.pdf"
        local_pdf_file_path = f"/tmp/{pdf_file_path}"
        pdfkit.from_url(pdf_data.kwargs["html_url"], local_pdf_file_path)

        # save pdf file
        pdf_url = self.storage_adapter.save(pdf_file_path, pdf_file_path)
        pdf_data.result = pdf_url
        pdf_data.status = "Complete"

        # update db record
        self.db_adapter.update(pdf_data.task_id, pdf_data)

        return pdf_data
