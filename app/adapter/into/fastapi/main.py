import os
from fastapi import FastAPI

from .routes import pdf

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")

app = FastAPI(root_path=f"/{ENVIRONMENT}")
app.include_router(pdf.router)


@app.get("/")
async def root():
    return {"message": "pdf generator service"}
