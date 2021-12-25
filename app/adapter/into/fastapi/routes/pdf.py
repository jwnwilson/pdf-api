from adapter.into.fastapi.dependencies import (
    get_db_adapater,
    get_storage_adapater,
    get_task_adapater,
)
from fastapi import APIRouter, Depends, HTTPException
from ports.pdf import PdfCreateData, PdfData, PdfGenerateData
from ports.storage import StorageData
from ports.task import TaskData
from use_case import create_pdf, generate_pdf_task, get_pdf_task

router = APIRouter(
    prefix="/pdf",
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_pdf_route(
    pdf_data: PdfCreateData,
    storage_adapter=Depends(get_storage_adapater),
    db_adapter=Depends(get_db_adapater),
) -> PdfData:
    # call create use case
    upload_data: StorageData = create_pdf.create_pdf(
        storage_adapter, db_adapter, pdf_data
    )
    # return pdf id with pdf job data
    return upload_data


@router.post("/{pdf_id}")
async def generate_pdf(
    pdf_id: str,
    pdf_data: PdfGenerateData,
    task_adapter=Depends(get_task_adapater),
    db_adapter=Depends(get_db_adapater),
) -> TaskData:
    pdf_data.pdf_id = pdf_id
    # call create use case
    pdf_task_data: TaskData = generate_pdf_task.generate_pdf_task(
        task_adapter, db_adapter, pdf_data
    )
    # return pdf id with pdf job data
    return pdf_task_data


@router.get("/{pdf_id}")
async def get_pdf(
    pdf_id: str,
    task_adapter=Depends(get_task_adapater),
    db_adapter=Depends(get_db_adapater),
) -> PdfData:
    # Attempt to get pdf data by id
    return get_pdf_task.get_pdf(task_adapter, db_adapter, pdf_id)
