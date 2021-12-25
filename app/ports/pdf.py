from typing import List

from pydantic import BaseModel


class PdfCreateData(BaseModel):
    html_url: str
    images_urls: List[str]


class PdfData(BaseModel):
    pdf_id: str
    html_url: str
    images_urls: List[str]


class PdfGenerateData(BaseModel):
    pdf_id: str
    params: dict
