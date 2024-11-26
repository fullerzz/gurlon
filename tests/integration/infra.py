import argparse
from typing import Literal

import boto3
from pydantic import BaseModel

REGION: Literal["us-west-1"] = "us-west-1"
TABLE_NAME = "gurlon-table"
BUCKET_NAME = "gurlon-bucket"


class ResourceInfo(BaseModel):
    name: str
    arn: str
    region: str


def create_dynamodb_table(session: boto3.Session) -> ResourceInfo:
    dynamodb = session.client("dynamodb", region_name=REGION)
    create_resp = dynamodb.create_table(
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        TableName=TABLE_NAME,
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
    waiter.wait(TableName=TABLE_NAME)
    dynamodb.update_continuous_backups(
        TableName=TABLE_NAME,
        PointInTimeRecoverySpecification={
            "PointInTimeRecoveryEnabled": True,
        },
    )
    # Validate we have the table ARN
    if "TableArn" not in create_resp["TableDescription"]:
        raise ValueError("Table ARN not found in response")
    return ResourceInfo(name=TABLE_NAME, arn=create_resp["TableDescription"]["TableArn"], region=REGION)


def create_s3_bucket(session: boto3.Session) -> ResourceInfo:
    s3 = session.client("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME, ACL="private", CreateBucketConfiguration={"LocationConstraint": REGION})
    waiter = s3.get_waiter("bucket_exists")
    waiter.wait(Bucket=BUCKET_NAME)
    return ResourceInfo(name=BUCKET_NAME, arn=f"arn:aws:s3:::{BUCKET_NAME}", region=REGION)


def log_resources(table: ResourceInfo, bucket: ResourceInfo) -> None:
    print(f"Created DynamoDB table: {table.name} ({table.arn}) in {table.region}")
    print(f"Created S3 bucket: {bucket.name} ({bucket.arn}) in {bucket.region}")


def create_infrastructure() -> None:
    session = boto3.Session(region_name=REGION)
    table = create_dynamodb_table(session)
    bucket = create_s3_bucket(session)
    log_resources(table, bucket)


def destroy_infrastructure() -> None:
    session = boto3.Session(region_name=REGION)
    table = session.client("dynamodb", region_name=REGION)
    table.delete_table(TableName=TABLE_NAME)
    bucket = session.client("s3", region_name=REGION)
    bucket.delete_bucket(Bucket=BUCKET_NAME)
    print(f"Deleted DynamoDB table: {TABLE_NAME}")
    print(f"Deleted S3 bucket: {BUCKET_NAME}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", type=str, choices=["create", "destroy"], required=True)
    args = parser.parse_args()
    if args.operation == "create":
        create_infrastructure()
    elif args.operation == "destroy":
        destroy_infrastructure()
    else:
        raise ValueError("Invalid operation")
