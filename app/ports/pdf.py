from typing import List, Optional

from pydantic import BaseModel


class PdfCreateData(BaseModel):
    html_url: str
    images_urls: List[str]


class PdfData(BaseModel):
    pdf_id: str
    html_url: str
    images_urls: Optional[List[str]]
    pdf_url: Optional[str]
    status: Optional[str]


class PdfGenerateData(BaseModel):
    pdf_id: str
    params: dict
