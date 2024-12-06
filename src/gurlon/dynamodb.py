# pyright: reportTypedDictNotRequiredAccess=false
from datetime import datetime
from zoneinfo import ZoneInfo

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.type_defs import DescribeTableOutputTypeDef
from pydantic import BaseModel


class TableMetadata(BaseModel):
    table_arn: str
    table_name: str
    table_status: str
    primary_key: str
    sort_key: str | None = None
    total_items: int
    total_size_bytes: int


def _build_table_metadata(data: DescribeTableOutputTypeDef) -> TableMetadata:
    table = data["Table"]
    try:
        return TableMetadata(
            table_arn=table["TableArn"],
            table_name=table["TableName"],
            table_status=table["TableStatus"],
            primary_key=table["KeySchema"][0]["AttributeName"],
            sort_key=table["KeySchema"][1]["AttributeName"] if len(table["KeySchema"]) > 1 else None,
            total_items=table["ItemCount"],
            total_size_bytes=table["TableSizeBytes"],
        )
    except (IndexError, KeyError) as e:
        raise ValueError("Invalid table metadata") from e


class DynamoTable:
    def __init__(self, table_name: str, region: str = "us-east-1") -> None:
        self.table_name = table_name
        # NOTE: This requires AWS credentials to be present locally by user
        self.client = boto3.client("dynamodb", region_name=region)
        self.metadata = self.get_metadata()

    def get_metadata(self) -> TableMetadata:
        response = self.client.describe_table(TableName=self.table_name)
        return _build_table_metadata(response)

    def export_to_s3(self, bucket: str, key_prefix: str) -> str:
        if len(key_prefix) < 3:
            raise ValueError("Key prefix must be at least 3 characters long")

        try:
            response = self.client.export_table_to_point_in_time(
                TableArn=self.metadata.table_arn,
                S3Bucket=bucket,
                ExportTime=datetime.now(ZoneInfo("UTC")),
                S3Prefix=key_prefix,
                ExportFormat="DYNAMODB_JSON",
                ExportType="FULL_EXPORT",
            )
        except ClientError as e:
            raise ValueError("Export failed") from e

        if response["ExportDescription"]["ExportStatus"] == "FAILED":
            raise ValueError("Export failed")

        return response["ExportDescription"]["ExportArn"]
