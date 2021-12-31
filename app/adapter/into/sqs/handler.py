import json
import logging
from typing import List
import traceback


from infrastructure.db import DynamodbAdapter
from infrastructure.storage import S3Adapter
from ports.pdf import PdfData, PdfGenerateData
from use_case import generate_pdf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def pdf_generator_lambda_handler(event, context) -> List[PdfGenerateData]:
    tasks_data = []
    records = event["Records"]

    logger.info(f"Processing {len(records)} record(s) from SQS")

    # Loops through every file uploaded
    for i, record in enumerate(event["Records"]):
        i = i + 1
        try:
            logger.info(f"Processing record {i} from SQS")
            # Parse event data
            pdf_gen_data = json.loads(record["body"])
            pdf_data = PdfData(
                html_url=pdf_gen_data["html_url"], images_urls=pdf_gen_data["image_urls"]
            )
            logger.info(f"PDF data {i} parsed from SQS, generating PDF")
            
            db_adapter = DynamodbAdapter({"table": "pdf_generation"})
            storage_adapter = S3Adapter({"bucket": "pdf_generation"})
            logger.info(f"PDF generating {i}")
            task_data = generate_pdf.generate_pdf(db_adapter, storage_adapter, pdf_data)
            logger.info(f"PDF generated {i}")

            tasks_data.append(task_data)
        except Exception as err:
            err_msg = traceback.format_exc()
            logger.error(f"PDF generation failed: {err_msg}, skipping")
    
    logger.info(f"Generated {len(tasks_data)} PDFs from SQS")

    return tasks_data