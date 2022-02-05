import os

from fastapi import FastAPI, Depends

from .routes import pdf_generation, pdf_template
from .dependencies import get_current_user

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")

root_prefix = f"/"

PROTECTED = [Depends(get_current_user)]

app = FastAPI(
    title="PDF Generator Service",
    description="Generate PDFs from templates",
    version="0.0.1",
    root_path=root_prefix,
)
app.include_router(
    pdf_template.router,
    dependencies=PROTECTED
)
app.include_router(
    pdf_generation.router,
    dependencies=PROTECTED
)


@app.get("/")
async def version():
    return {"message": "pdf generator service"}
