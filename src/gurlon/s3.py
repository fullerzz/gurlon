# pyright: reportTypedDictNotRequiredAccess=false
# ruff: noqa: N815
from datetime import datetime
from pathlib import Path

import boto3
from pydantic import BaseModel


class ManifestFile(BaseModel):
    itemCount: int
    md5Checksum: str
    etag: str
    dataFileS3Key: str


class ManifestSummary(BaseModel):
    version: str
    exportArn: str
    startTime: datetime
    endTime: datetime
    tableArn: str
    tableId: str
    exportTime: datetime
    s3Bucket: str
    s3Prefix: str
    s3SseAlgorithm: str
    s3SseKmsKeyId: str | None
    manifestFilesS3Key: str
    billedSizeBytes: int
    itemCount: int
    outputFormat: str


class DynamoExport(BaseModel):
    arn: str
    local_data_dir: Path
    manifest_files: list[ManifestFile]
    manifest_summary: ManifestSummary


def _parse_manifest_summary(path: Path) -> ManifestSummary:
    with path.open("r") as f:
        manifest_summary = ManifestSummary.model_validate_json(f.read())
    return manifest_summary


def _parse_manifest_files(path: Path) -> list[ManifestFile]:
    manifest_files: list[ManifestFile] = []
    with path.open("r") as f:
        for line in f.readlines():
            manifest_files.append(ManifestFile.model_validate_json(line))  # noqa: PERF401
    return manifest_files


class S3Bucket:
    def __init__(self, bucket_name: str, aws_region: str = "us-east-1") -> None:
        self.bucket_name = bucket_name
        # NOTE: This requires AWS credentials to be present locally by user
        self.client = boto3.client("s3", region_name=aws_region)

    def download_export(self, download_dir: Path, table_export_arn: str, key_prefix: str) -> DynamoExport:
        # First, need to find the latest export in the bucket
        resp = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{key_prefix}/AWSDynamoDB/")
        if "Contents" not in resp:
            print(resp)
            raise ValueError("No exports found in bucket")
        print(resp["Contents"])
        # TODO: Extract export ID/key from resp then use it to download the manifest files
        manifest_key: str | None = None
        for obj in resp["Contents"]:
            if obj["Key"].endswith("manifest-summary.json"):
                manifest_key = obj["Key"]
                break
        if manifest_key is None:
            raise ValueError("No manifest-summary.json found in bucket")
        self.client.download_file(
            Bucket=self.bucket_name,
            Key=manifest_key,  # TODO: Extract the key from the response
            # gurlon/AWSDynamoDB/01732662110643-26e512e8/manifest-files.json
            Filename=(download_dir / "manifest-summary.json").as_posix(),
        )
        # Download manifest-files.json
        self.client.download_file(
            Bucket=self.bucket_name,
            Key=manifest_key.replace("manifest-summary", "manifest-files", 1),
            # gurlon/AWSDynamoDB/01732662110643-26e512e8/manifest-files.json
            Filename=(download_dir / "manifest-files.json").as_posix(),
        )
        # Iterate over objects in Contents and download the manifest files

        manifest_summary = _parse_manifest_summary(download_dir / "manifest-summary.json")
        manifest_files = _parse_manifest_files(download_dir / "manifest-files.json")
        return DynamoExport(
            arn=table_export_arn,
            local_data_dir=download_dir,
            manifest_files=manifest_files,
            manifest_summary=manifest_summary,
        )
