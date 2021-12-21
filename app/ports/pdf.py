from pydantic import BaseModel


class PdfInData(BaseModel):
    html_url: str
