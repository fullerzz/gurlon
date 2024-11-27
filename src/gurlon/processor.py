import gzip
from pathlib import Path

from gurlon.dynamodb import DynamoTable
from gurlon.s3 import DynamoExport, S3Bucket


class DataExporter:
    def __init__(self, aws_region: str, table_name: str, bucket_name: str, key_prefix: str = "gurlon") -> None:
        self.aws_region = aws_region
        self.table: DynamoTable = DynamoTable(table_name, aws_region)
        self.bucket: S3Bucket = S3Bucket(bucket_name, aws_region)
        self.table_export_arn: str | None = None
        self.key_prefix = key_prefix

    def export_data(self) -> str:
        # Export DynamoDB table data to S3
        self.table_export_arn = self.table.export_to_s3(self.bucket.bucket_name, self.key_prefix)
        return self.table_export_arn

    def download_data(self) -> str:
        if not self.table_export_arn:
            raise ValueError("No export ARN found. Run export_data first")

        # Download data from S3
        download_dir = Path.home() / "Downloads" / "dynamodb_exports"
        download_dir.mkdir(exist_ok=True)
        export = self.bucket.download_export(download_dir, self.table_export_arn, self.key_prefix)
        # Now we have the exported data downloaded locally...
        # Uncompress the downloaded files
        self.uncompress_data(export)
        # Optional: Validate the data
        # Save as CSV or other format
        return "foo"

    def uncompress_data(self, export_metadata: DynamoExport) -> None:
        # Uncompress the downloaded files
        for data_file in export_metadata.local_data_files:
            with gzip.open(data_file.as_posix(), "rb") as f:
                content = f.read()
            with Path(data_file.as_posix().replace(".gz", "")).open("wb") as f:
                f.write(content)
        pass
