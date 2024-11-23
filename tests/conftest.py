import os
from collections.abc import Generator
from typing import Any

import boto3
import pytest
from moto import mock_aws
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_s3 import S3Client


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
    return table_name
