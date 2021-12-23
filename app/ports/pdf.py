from pydantic import BaseModel
from typing import List


class PdfCreateData(BaseModel):
    html_url: str
    images_urls: List[str]


class PdfData(BaseModel):
    pdf_uuid: str
    html_url: str
    images_urls: List[str]


class PdfGenerateData(BaseModel):
    pdf_uuid: str
    params: dict
