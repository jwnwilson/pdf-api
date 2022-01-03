from typing import List, Optional

from pydantic import BaseModel


class PdfCreateInData(BaseModel):
    pdf_id: str


class PdfUploadInData(BaseModel):
    pdf_id: str
    file_name: str


class PdfCreateOutData(BaseModel):
    pdf_id: str
    upload_url: str
    upload_fields: dict


class PdfData(BaseModel):
    pdf_id: str
    html_url: str
    images_urls: Optional[List[str]]


class PdfGenerateDataIn(BaseModel):
    pdf_id: str
    params: dict


class PdfGenerateData(BaseModel):
    pdf_id: str
    task_id: Optional[str]
    params: Optional[dict]
    pdf_url: Optional[str]
    status: Optional[str]
