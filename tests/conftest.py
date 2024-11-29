import os
from collections.abc import Generator
from pathlib import Path
from typing import Any, Literal

import boto3
import pytest
from faker import Faker
from moto import mock_aws
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_dynamodb.type_defs import ExportTableToPointInTimeOutputTypeDef
from mypy_boto3_s3 import S3Client
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from pydantic import BaseModel

from gurlon.dynamodb import DynamoTable

MOCK_EXPORT_ARN = "arn:aws:dynamodb:us-west-1:863881196012:table/gurlon-table/export/01732662110643-26e512e8"


class TableMetadata(BaseModel):
    table_name: str
    primary_key: str
    sort_key: str | None = None
    total_items: int


class TableItem(BaseModel):
    user_id: str
    user_name: str
    email: str
    role: str
    full_name: str


class TableMetadataFactory(ModelFactory[TableMetadata]):
    table_name = Use(ModelFactory.__faker__.name)


class TableItemFactory(ModelFactory[TableItem]):
    user_id = Use(ModelFactory.__faker__.uuid4)
    user_name = Use(ModelFactory.__faker__.user_name)
    email = Use(ModelFactory.__faker__.email)
    role = Use(ModelFactory.__faker__.random_element, elements=("admin", "user"))
    full_name = Use(ModelFactory.__faker__.name)


table_item_factory = register_fixture(TableItemFactory)
table_metadata_factory = register_fixture(TableMetadataFactory)


@pytest.fixture(autouse=True)
def mock_export_pitr(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_export_table_to_point_in_time(*args: Any, **kwargs: Any) -> str:
        resp: ExportTableToPointInTimeOutputTypeDef = {
            "ExportDescription": {
                "ExportArn": MOCK_EXPORT_ARN,
                "ExportStatus": "IN_PROGRESS",
            },
            "ResponseMetadata": {
                "RequestId": "12345678901234567890123456789012",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "server": "Server",
                    "date": "Mon, 01 Nov 2021 00:00:00 GMT",
                    "content-type": "application/x-amz-json-1.0",
                    "content-length": "123",
                    "connection": "keep-alive",
                    "x-amzn-requestid": "12345678901234567890123456789012",
                },
                "RetryAttempts": 0,
            },
        }
        return resp["ExportDescription"]["ExportArn"]  # pyright: ignore[reportTypedDictNotRequiredAccess]

    monkeypatch.setattr(DynamoTable, "export_to_s3", mock_export_table_to_point_in_time)


@pytest.fixture(autouse=True)
def faker_seed() -> Literal[1]:
    return 1


@pytest.fixture(autouse=True)
def seed_factories(faker: Faker, faker_seed: Literal[1]) -> None:
    ModelFactory.__faker__ = faker
    ModelFactory.__random__.seed(faker_seed)


@pytest.fixture
def table_items(table_item_factory: TableItemFactory) -> list[TableItem]:
    return table_item_factory.batch(10)


@pytest.fixture
def aws_creds() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"  # noqa: S105
    os.environ["AWS_SECURITY_TOKEN"] = "testing"  # noqa: S105
    os.environ["AWS_SESSION_TOKEN"] = "testing"  # noqa: S105
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3(aws_creds: None) -> Generator[S3Client, Any, None]:
    """
    Return a mocked S3 client
    """
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def s3_bucket(s3: S3Client) -> str:
    """
    Create a bucket for testing
    """
    bucket_name = "test-bucket"
    s3.create_bucket(Bucket=bucket_name)
    waiter = s3.get_waiter("bucket_exists")
    waiter.wait(Bucket=bucket_name)
    return bucket_name


@pytest.fixture
def dynamodb(aws_creds: None) -> Generator[DynamoDBClient, Any, None]:
    """
    Return a mocked DynamoDB client
    """
    with mock_aws():
        yield boto3.client("dynamodb", region_name="us-east-1")


@pytest.fixture
def dynamodb_table(dynamodb: DynamoDBClient) -> str:
    """
    Create a table for testing
    """
    table_name = "test-table"
    dynamodb.create_table(
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        BillingMode="PAY_PER_REQUEST",
        # Stream needs to be enabled in order to perform PITR export to S3
        StreamSpecification={
            "StreamEnabled": True,
            "StreamViewType": "NEW_AND_OLD_IMAGES",
        },
        TableClass="STANDARD",
        DeletionProtectionEnabled=False,
    )
    # Once table exists, enable PITR
    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=table_name)
    dynamodb.update_continuous_backups(
        TableName=table_name,
        PointInTimeRecoverySpecification={
            "PointInTimeRecoveryEnabled": True,
        },
    )
    return table_name


@pytest.fixture
def populated_table(dynamodb_table: str, table_items: list[TableItem]) -> str:
    table_name = dynamodb_table
    table = boto3.resource("dynamodb").Table(table_name)
    for item in table_items:
        table.put_item(Item=item.model_dump())
    assert table.item_count == len(table_items)
    return table_name


@pytest.fixture
def populated_bucket(s3_bucket: str) -> str:
    client = boto3.client("s3")
    prefix = "tests/data/mock_export_contents/"
    for root, _dirs, files in Path("tests/data/mock_export_contents").walk():
        for file in files:
            key = os.path.join(root, file).replace(prefix, "")
            client.upload_file(
                Filename=os.path.join(root, file),
                Bucket=s3_bucket,
                Key=key,
            )
    return s3_bucket
