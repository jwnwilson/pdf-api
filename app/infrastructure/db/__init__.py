from copy import deepcopy

import boto3
from ports.db import DbAdapter


class DynamodbAdapter(DbAdapter):
    def __init__(self, config: dict):
        # Get the service resource.
        self.client = boto3.resource("dynamodb")
        self.table = self.client.Table(config["table"])

    def read(self, record_id: str):
        return self.table.get_item(Key={"task_id": record_id})

    def create(self, record_data: dict):
        return self.table.put_item(Item=record_data)

    def update(self, record_id: str, record_data: dict):
        update_expression = "SET "
        expression_attr_values = {}
        expression_attr_names = {}
        update_expressions = []

        for key in record_data.keys():
            update_expressions.append(f"#{key} = :{key}")
            expression_attr_values[f":{key}"] = record_data[key]
            expression_attr_names[f"#{key}"] = key

        update_expression += ", ".join(update_expressions)

        return self.table.update_item(
            Key={"task_id": record_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attr_values,
            ExpressionAttributeNames=expression_attr_names,
        )
