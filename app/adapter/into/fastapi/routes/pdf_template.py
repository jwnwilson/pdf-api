import logging
from typing import List

from adapter.into.fastapi.dependencies import (
    get_db_adapater,
    get_task_storage_adapter,
    get_template_storage_adapter,
)
from fastapi import APIRouter, Depends, HTTPException
from ports.pdf import PdfCreateInData, PdfCreateOutData, PdfUploadInData
from use_case import create_pdf as create_pdf_uc
from use_case import list_pdf as list_pdf_uc

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pdf",
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def list_pdf_templates(
    template_storage_adapter=Depends(get_template_storage_adapter),
    task_storage_adapter=Depends(get_task_storage_adapter),
    db_adapter=Depends(get_db_adapater),
) -> List[str]:
    # call create use case
    pdfs: List[str] = list_pdf_uc.list_pdf(
        db_adapter,
        task_storage_adapter=task_storage_adapter,
        template_storage_adapter=template_storage_adapter,
    )
    # return pdf id with pdf job data
    return pdfs


@router.post("/")
async def create_pdf_template(
    pdf_data: PdfCreateInData,
    template_storage_adapter=Depends(get_template_storage_adapter),
    task_storage_adapter=Depends(get_task_storage_adapter),
    db_adapter=Depends(get_db_adapater),
) -> PdfCreateOutData:
    # call create use case
    return create_pdf_uc.create_pdf(
        db_adapter, task_storage_adapter, template_storage_adapter, pdf_data
    )


@router.post("/upload")
async def upload_template_static(
    pdf_data: PdfUploadInData,
    template_storage_adapter=Depends(get_template_storage_adapter),
    task_storage_adapter=Depends(get_task_storage_adapter),
    db_adapter=Depends(get_db_adapater),
) -> PdfCreateOutData:
    # call create use case
    return create_pdf_uc.upload_static(
        db_adapter, task_storage_adapter, template_storage_adapter, pdf_data
    )
