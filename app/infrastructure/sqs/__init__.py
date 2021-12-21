import json

import boto3
from ports.task import TaskAdapter, TaskArgs, TaskData


class SqsTaskAdapter(TaskAdapter):
    def __init__(self, config):
        # Create SQS client
        self.sqs = boto3.client("sqs")
        self.queue_url = config["queue"]

    def create_task(self, task_name: str, task_args: TaskArgs) -> TaskData:
        # Send message to SQS queue
        task_data = {"task_name": task_name, "task_args": task_args.dict()}
        sqs_resp = self.sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=(json.dumps(task_data))
        )

        resp = TaskData(task_id=sqs_resp["MessageId"], status="pending", data=sqs_resp)

        return resp

    def get_task(self) -> TaskData:
        # Get a message from sqs queue
        sqs_resp = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=0,
            WaitTimeSeconds=0,
        )

        return TaskData(
            task_id=sqs_resp["MessageId"], status="processing", data=sqs_resp
        )
