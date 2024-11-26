# pyright: reportTypedDictNotRequiredAccess=false

from pathlib import Path

import boto3


class S3Bucket:
    def __init__(self, bucket_name: str, export_key_prefix: str = "", aws_region: str = "us-east-1") -> None:
        self.bucket_name = bucket_name
        self.prefix = export_key_prefix
        # NOTE: This requires AWS credentials to be present locally by user
        self.client = boto3.client("s3", region_name=aws_region)

    def download_export(self, download_dir: Path) -> None:
        # First, need to find the latest export in the bucket
        resp = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix)
        if "Contents" not in resp:
            raise ValueError("No exports found in bucket")
        print(resp["Contents"])
