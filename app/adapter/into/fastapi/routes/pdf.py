import logging
from typing import List

from adapter.into.fastapi.dependencies import (
    get_db_adapater,
    get_template_storage_adapater,
)
from fastapi import APIRouter, Depends, HTTPException
from ports.pdf import PdfCreateData, PdfData, PdfGenerateData
from ports.storage import StorageData
from ports.task import TaskArgs, TaskData
from use_case import create_pdf as create_pdf_uc
from use_case import generate_pdf_task, get_pdf_task
from use_case import list_pdf as list_pdf_uc

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pdf",
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def list_pdf_templates(
    storage_adapter=Depends(get_template_storage_adapater),
    db_adapter=Depends(get_db_adapater),
) -> List[str]:
    # call create use case
    pdfs: List[str] = list_pdf_uc.list_pdf(db_adapter, storage_adapter)
    # return pdf id with pdf job data
    return pdfs


@router.post("/")
async def create_pdf_template(
    pdf_data: PdfCreateData,
    storage_adapter=Depends(get_template_storage_adapater),
    db_adapter=Depends(get_db_adapater),
) -> PdfData:
    # call create use case
    upload_data: StorageData = create_pdf_uc.create_pdf(
        db_adapter, storage_adapter, pdf_data
    )
    # return pdf id with pdf job data
    return upload_data
