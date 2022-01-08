import json
import logging
import os
import traceback
from typing import List

from infrastructure.db import DynamodbAdapter
from infrastructure.storage import S3Adapter
from ports.pdf import PdfGenerateData
from ports.user import UserData
from use_case import generate_pdf

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

ENVIRONMENT = os.environ["ENVIRONMENT"]


def pdf_generator_lambda_handler(event, context) -> List[PdfGenerateData]:
    tasks_data = []
    records = event["Records"]

    logger.info(f"Processing {len(records)} record(s) from SQS")

    # Loops through every file uploaded
    for i, record in enumerate(event["Records"]):
        i = i + 1
        try:
            logger.info(f"Processing record {i} from SQS")
            # Get pdf uuid to fetch files
            pdf_gen_data = json.loads(record["body"])
            user = UserData(
                user_id=pdf_gen_data["user_id"]
            )

            pdf_data = PdfGenerateData(
                pdf_id=pdf_gen_data["params"],
                params=pdf_gen_data["params"],
                task_id=pdf_gen_data["task_id"],
            )

            logger.info(f"PDF id:{pdf_data.pdf_id} parsed from SQS, generating PDF")
            db_adapter = DynamodbAdapter(
                {"table": f"pdf_task_{ENVIRONMENT}"},
                user=user
            )
            pdf_storage_adapter = S3Adapter(
                {"bucket": f"jwnwilson-pdf-task-{ENVIRONMENT}"},
                user=user
            )
            template_storage_adapter = S3Adapter(
                {"bucket": f"jwnwilson-pdf-template-{ENVIRONMENT}"},
                user=user
            )
            task_data = generate_pdf.generate_pdf(
                db_adapter, template_storage_adapter, pdf_storage_adapter, pdf_data
            )
            logger.info(f"PDF generated {pdf_data.pdf_id}")

            tasks_data.append(task_data)
        except Exception as err:
            err_msg = traceback.format_exc()
            logger.error(f"PDF generation failed: {err_msg}, skipping")

    logger.info(f"Generated {len(tasks_data)} PDFs from SQS")

    return tasks_data
