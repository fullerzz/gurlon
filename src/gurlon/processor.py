from pathlib import Path

from gurlon.dynamodb import DynamoTable
from gurlon.s3 import S3Bucket


class DataExporter:
    def __init__(self, aws_region: str, table_name: str, bucket_name: str) -> None:
        self.aws_region = aws_region
        self.table: DynamoTable = DynamoTable(table_name, aws_region)
        self.bucket: S3Bucket = S3Bucket(bucket_name, aws_region)

    def export_data(self, key_prefix: str = "gurlon") -> str:
        # Export DynamoDB table data to S3
        export_arn = self.table.export_to_s3(self.bucket.bucket_name, key_prefix)
        return export_arn

    def download_data(self) -> str:
        # Download data from S3
        download_dir = Path.home() / "Downloads" / "dynamodb_exports"
        self.bucket.download_export(download_dir)
        # Now we have the exported data downloaded locally...
        # Uncompress the downloaded files
        # Optional: Validate the data
        # Save as CSV or other format
        return "foo"
