import boto3
from ports.db import DbAdapter


class DynamodbAdapter(DbAdapter):
    def __init__(self, config: dict):
        # Get the service resource.
        self.client = boto3.resource("dynamodb")
        self.table = self.client.Table(config["table"])

    def update(self, record_id: str, record_data: dict):
        return self.table.update_item(
            Key={"pkey": record_id},
            AttributeUpdates=record_data,
        )
