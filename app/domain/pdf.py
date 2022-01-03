import logging
import re
import uuid
from typing import List

import pdfkit
import requests
from jinja2 import Environment, FileSystemLoader
from ports.db import DbAdapter
from ports.pdf import (
    PdfCreateInData,
    PdfCreateOutData,
    PdfData,
    PdfGenerateData,
    PdfUploadInData,
)
from ports.storage import StorageAdapter
from ports.task import TaskAdapter, TaskData

logger = logging.getLogger(__name__)


def save_url_to_storage(storage_adapter, pdf_id, url, file_name=None) -> str:
    """Download file from url and save it locally

    Args:
        storage_adapter ([type]): [description]
        pdf_id ([type]): [description]
        url ([type]): [description]
        file_name ([type], optional): [description]. Defaults to None.

    Returns:
        str: [description]
    """
    # Download file
    file_response = requests.get(url)
    # Get file name from url file name or use url path
    if not file_name:
        file_name = get_file_name(url, file_response)
    file_path = f"{pdf_id}/{file_name}.html"
    local_html_path = "/tmp/" + file_path

    with open(local_html_path, "w") as file:
        file.write(file_response.text)

    # Save in our storage adapter
    storage_adapter.save(local_html_path, file_path)

    return file_path


def get_file_name(url, response) -> str:
    fname = ""
    if "Content-Disposition" in response.headers.keys():
        fname = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        fname = url.split("/")[-1]

    return fname


class PdfTemplateEntity:
    def __init__(
        self,
        db_adapter: DbAdapter,
        template_storage_adapter: StorageAdapter,
    ):
        self.db_adapter = db_adapter
        self.template_storage_adapter = template_storage_adapter

    def create_pdf_template(self, pdf_data: PdfCreateInData) -> PdfCreateOutData:
        """[summary]

        Args:
            pdf_data (PdfData): [description]

        Returns:
            PdfGenerateData: [description]
        """
        return self.upload_static(
            PdfUploadInData(pdf_id=pdf_data.pdf_id, file_name="template.html")
        )

    def upload_static(self, pdf_data: PdfUploadInData) -> PdfCreateOutData:
        upload_template_path = f"{pdf_data.pdf_id}/{pdf_data.file_name}"
        upload_url = self.template_storage_adapter.upload_url(upload_template_path)

        return PdfCreateOutData(
            pdf_id=pdf_data.pdf_id,
            upload_url=upload_url.upload_url,
            upload_fields=upload_url.fields,
        )

    def list_pdf_templates(self) -> List[str]:
        """List pdf templates to choose from"""
        folders: List[str] = self.template_storage_adapter.list("/")
        return folders


# TODO: Break into pdf template and pdf entities
class PdfEntity:
    def __init__(
        self,
        db_adapter: DbAdapter,
        template_storage_adapter: StorageAdapter,
        task_storage_adapter: StorageAdapter,
    ):
        self.db_adapter = db_adapter
        self.template_storage_adapter = template_storage_adapter
        self.task_storage_adapter = task_storage_adapter

    def get_pdf(self, uuid: str) -> PdfData:
        logger.info(f"Getting pdf data: {uuid}")
        # Get image files from storage
        path = f"{uuid}/"
        files = self.template_storage_adapter.list(path)
        try:
            html_path = [x for x in files if x.endswith("html")][0]
            image_urls = [x for x in files if not x.endswith("html")]
        except IndexError:
            logger.error(f"Unable to find template html file for pdf: {uuid}")
            raise

        logger.info(f"Got pdf data: {uuid}")
        logger.info(f"Html pdf data: {html_path}")
        logger.info(f"Image pdf data: {image_urls}")
        return PdfData(pdf_id=uuid, html_url=html_path, image_urls=image_urls)

    def generate_html(self, template_url: str, params: dict) -> str:
        """[summary]

        Args:
            pdf_data (PdfData): [description]

        Returns:
            str: [description]
        """
        # Save html template data to file
        html_template_path = "/tmp/template.html"
        html_generated_path = "/tmp/generated.html"
        html_template_data = requests.get(template_url)
        # save html template
        with open(html_template_path, "w") as fh:
            fh.write(html_template_data.text)

        jinja_env = Environment(loader=FileSystemLoader("/tmp"))
        template = jinja_env.get_template("template.html")
        output_from_parsed_template = template.render(**params)

        # save generated html
        with open(html_generated_path, "w") as fh:
            fh.write(output_from_parsed_template)

        return html_generated_path

    def generate_pdf(self, pdf_gen_data: PdfGenerateData) -> PdfGenerateData:
        """[summary]

        Args:
            html (str): [description]
            file_path (str): [description]

        Returns:
            [type]: [description]
        """
        task_id = pdf_gen_data.task_id
        # get pdf data from uuid
        pdf_data = self.get_pdf(pdf_gen_data.pdf_id)

        # generate html from template + parameters
        html_path = self.generate_html(pdf_data.html_url, pdf_gen_data.params)

        # Create local folders if needed
        local_file_folder = f"/tmp/"
        local_file_path = local_file_folder + "render.pdf"

        # Render pdf file
        logger.info(f"Rendering PDF task: {task_id}, pdf_id: {pdf_gen_data.pdf_id}")
        pdfkit.from_file(html_path, local_file_path)
        logger.info(f"Rendered PDF task: {task_id}, pdf_id: {pdf_gen_data.pdf_id}")

        # save pdf file
        logger.info(f"Saving PDF task: {task_id} to storage")
        pdf_file_path = f"{task_id}/render.pdf"
        storage_data = self.task_storage_adapter.save(local_file_path, pdf_file_path)
        logger.info(f"Saved PDF task: {task_id} to storage")

        # update task db record
        pdf_gen_data.pdf_url = storage_data.path
        pdf_gen_data.status = "Complete"

        logger.info(f"Updating PDF task: {task_id} DB record")
        self.db_adapter.create(pdf_gen_data.dict())
        logger.info(f"Updated PDF task: {task_id} DB record")

        return pdf_gen_data.dict()
