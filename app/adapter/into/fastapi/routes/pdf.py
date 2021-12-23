from adapter.into.fastapi.dependencies import get_db_adapater, get_task_adapater, get_storage_adapater
from fastapi import APIRouter, Depends, HTTPException
from ports.pdf import PdfInData
from ports.task import TaskData
from ports.storage import StorageData
from use_case import create_pdf_task, get_pdf_task, upload_html, upload_image

router = APIRouter(
    prefix="/pdf",
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload_asset")
async def upload_asset(
    pdf_data: PdfInData,
    storage_adapter=Depends(get_storage_adapater),
    db_adapter=Depends(get_db_adapater),
):
    # call create use case
    upload_data: StorageData = upload_html(storage_adapter, db_adapter, pdf_data)
    # return pdf id with pdf job data
    return upload_data


@router.post("/")
async def create_pdf(
    pdf_data: PdfInData,
    task_adapter=Depends(get_task_adapater),
    db_adapter=Depends(get_db_adapater),
):
    # call create use case
    pdf_task_data: TaskData = create_pdf_task(task_adapter, db_adapter, pdf_data)
    # return pdf id with pdf job data
    return pdf_task_data


@router.get("/{pdf_id}")
async def get_pdf(
    pdf_id: str,
    task_adapter=Depends(get_task_adapater),
    db_adapter=Depends(get_db_adapater),
):
    # Attempt to get pdf data by id
    return get_pdf_task(task_adapter, db_adapter, pdf_id)
