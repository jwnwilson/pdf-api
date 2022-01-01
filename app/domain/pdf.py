import re
import uuid
import logging
import os

import pdfkit
import requests
from ports.db import DbAdapter
from ports.pdf import PdfData, PdfGenerateData
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskData

logger = logging.getLogger(__name__)


class PdfEntity:
    def __init__(self, db_adapter: DbAdapter, storage_adapter: StorageAdapter):
        self.db_adapter = db_adapter
        self.storage_adapter = storage_adapter

    def _get_file_name(self, url, response) -> str:
        fname = ""
        if "Content-Disposition" in response.headers.keys():
            fname = re.findall(
                "filename=(.+)", response.headers["Content-Disposition"]
            )[0]
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
        html_path = self._save_url_to_file(
            pdf_id, pdf_data.html_url, file_name="template.html"
        )

        # Download images and save in storage
        image_urls = []
        for image_url in pdf_data.images_urls:
            image_urls.append(self._save_url_to_file(pdf_id, image_url))

        # Return pdf data
        return PdfGenerateData(pdf_id=pdf_id)

    def get_pdf(self, uuid: str) -> PdfData:
        logger.info(f"Getting pdf data: {uuid}")
        # Get image files from storage
        path = f"{uuid}/"
        files = self.storage_adapter.list(path)
        try:
            html_path = [x for x in files if x.endswith("html")][0]
            image_urls = [x for x in files if not x.endswith("html")]
        except IndexError:
            logger.error(f"Unable to find html file for pdf: {uuid}")
            raise

        logger.info(f"Got pdf data: {uuid}")
        logger.info(f"Html pdf data: {html_path}")
        logger.info(f"Image pdf data: {image_urls}")
        return PdfData(pdf_id=uuid, html_url=html_path, image_urls=image_urls)

    def generate_pdf(self, pdf_gen_data: PdfGenerateData) -> PdfGenerateData:
        """[summary]

        Args:
            html (str): [description]
            file_path (str): [description]

        Returns:
            [type]: [description]
        """
        # get pdf data from uuid
        pdf_data = self.get_pdf(pdf_gen_data.pdf_id)

        # render pdf file
        local_file_folder = f"/tmp/{pdf_gen_data.pdf_id}"
        local_file_path = local_file_folder + "/render.pdf"
        if not os.path.exists(local_file_folder):
            os.makedirs(local_file_folder)

        logger.info(f"Rendering PDF {pdf_gen_data.pdf_id}")
        pdfkit.from_url(pdf_data.html_url, local_file_path)
        logger.info(f"Rendered PDF {pdf_gen_data.pdf_id}")

        # save pdf file
        logger.info(f"Saving PDF {pdf_gen_data.pdf_id} to storage")
        pdf_file_path = f"{pdf_gen_data.pdf_id}/render.html"
        pdf_url = self.storage_adapter.save(local_file_path, pdf_file_path)
        pdf_data.pdf_url = pdf_url
        pdf_data.status = "Complete"
        logger.info(f"Saved PDF {pdf_gen_data.pdf_id} to storage")

        # update db record
        logger.info(f"Updating PDF {pdf_gen_data.pdf_id} DB record")
        self.db_adapter.update(pdf_data.task_id, pdf_data)
        logger.info(f"Updated PDF {pdf_gen_data.pdf_id} DB record")

        return pdf_data
