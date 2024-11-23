import boto3
from pydantic import BaseModel


class TableMetadata(BaseModel):
    table_name: str
    primary_key: str
    sort_key: str | None = None
    total_items: int
    total_size_bytes: int


class DynamoTable:
    def __init__(self, table_name: str):
        self.table_name = table_name
        # NOTE: This requires AWS credentials to be present locally by user
        self.client = boto3.client("dynamodb")
        self.metadata = self.get_metadata()

    def get_metadata(self) -> TableMetadata:
        response = self.client.describe_table(TableName=self.table_name)
        table = response["Table"]
        return TableMetadata(
            table_name=table["TableName"],  # type: ignore
            primary_key=table["KeySchema"][0]["AttributeName"],  # type: ignore
            sort_key=table["KeySchema"][1]["AttributeName"]  # type: ignore
            if len(table["KeySchema"]) > 1  # type: ignore
            else None,
            total_items=table["ItemCount"],  # type: ignore
            total_size_bytes=table["TableSizeBytes"],  # type: ignore
        )
