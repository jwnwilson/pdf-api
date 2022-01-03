import os

from fastapi import FastAPI

from .routes import pdf_generation, pdf_template

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")

root_prefix = f"/"

app = FastAPI(
    title="PDF Generator Service",
    description="Generate PDFs from templates",
    version="0.0.1",
    root_path=root_prefix,
)
app.include_router(pdf_template.router)
app.include_router(pdf_generation.router)


@app.get("/")
async def version():
    return {"message": "pdf generator service"}
