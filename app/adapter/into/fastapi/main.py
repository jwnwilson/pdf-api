import os

from fastapi import FastAPI

from .routes import pdf, pdf_gen

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")
IS_LAMBDA = os.environ.get("AWS_EXECUTION_ENV") is not None

root_prefix = f"/{ENVIRONMENT}" if IS_LAMBDA else "/"

app = FastAPI(root_path=root_prefix)
app.include_router(pdf.router)
app.include_router(pdf_gen.router)


@app.get("/")
async def version():
    return {"message": "pdf generator service"}
