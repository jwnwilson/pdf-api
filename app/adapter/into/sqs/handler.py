import json

import boto3
from infrastructure.db import DynamodbAdapter
from infrastructure.storage import S3Adapter
from ports.pdf import PdfData
from use_case import generate_pdf


def pdf_generator_lambda_handler(event, context):

    # Loops through every file uploaded
    for record in event["Records"]:
        pdf_gen_data = json.loads(record["body"])
        pdf_data = PdfData(
            html_url=pdf_gen_data["html_url"], images_urls=pdf_gen_data["images_urls"]
        )
        db_adapter = DynamodbAdapter({"table": "pdf_generation"})
        storage_adapter = S3Adapter({"bucket": "pdf_generation"})

        task_data = generate_pdf.generate_pdf(db_adapter, storage_adapter, pdf_data)
