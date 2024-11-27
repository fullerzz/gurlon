import gzip
from collections.abc import Generator
from pathlib import Path
from typing import Any

import duckdb
import orjson
import structlog
from dynamodb_json import json_util

from gurlon.dynamodb import DynamoTable
from gurlon.s3 import DynamoExport, S3Bucket

log: structlog.stdlib.BoundLogger = structlog.get_logger()


class DataExporter:
    def __init__(self, aws_region: str, table_name: str, bucket_name: str, key_prefix: str = "gurlon") -> None:
        log.debug("Initializing DataExporter", aws_region=aws_region, table_name=table_name, bucket_name=bucket_name)
        self.aws_region = aws_region
        self.table: DynamoTable = DynamoTable(table_name, aws_region)
        self.bucket: S3Bucket = S3Bucket(bucket_name, aws_region)
        self.table_export_arn: str | None = None
        self.key_prefix = key_prefix
        self.export_metadata: DynamoExport | None = None
        self.decompressed_files: list[Path] = []

    def export_data(self) -> str:
        log.debug("Exporting data to S3", table_name=self.table.table_name, bucket_name=self.bucket.bucket_name)
        # Export DynamoDB table data to S3
        self.table_export_arn = self.table.export_to_s3(self.bucket.bucket_name, self.key_prefix)
        return self.table_export_arn

    def download_data(self) -> Path:
        if not self.table_export_arn:
            raise ValueError("No export ARN found. Run export_data first")
        # Download data from S3
        download_dir = Path.home() / "Downloads" / "dynamodb_exports"
        download_dir.mkdir(exist_ok=True)
        log.debug(
            "Downloading data from S3",
            table_name=self.table.table_name,
            bucket_name=self.bucket.bucket_name,
            local_dir=download_dir,
        )
        self.export_metadata = self.bucket.download_export(download_dir, self.table_export_arn, self.key_prefix)
        # Uncompress the downloaded files
        self.decompress_data()
        # Combine the data into a single file
        combined_path = self.combine_data()
        # Optional: Validate the data
        # Save as CSV or other format
        log.info("Data downloaded, decompressed, and combined into a single file", combined_path=combined_path)
        return combined_path

    def decompress_data(self) -> None:
        if not self.export_metadata:
            raise ValueError("No export metadata found. Run download_data first")
        log.debug("Decompressing downloaded data", local_dir=self.export_metadata.local_data_dir)
        # Uncompress the downloaded files
        for data_file in self.export_metadata.local_data_files:
            log.debug("Decompressing file", file=data_file)
            with gzip.open(data_file.as_posix(), "rb") as f:
                content = f.read()
            decompressed_file = Path(data_file.as_posix().replace(".gz", ""))
            with decompressed_file.open("wb") as f:
                f.write(content)
            self.decompressed_files.append(decompressed_file)

    def _read_raw_data(self) -> Generator[str, Any, None]:
        for file in self.decompressed_files:
            log.debug("Reading raw data from file", file=file)
            with file.open("r") as f:
                lines = f.readlines()
            yield from lines

    def combine_data(self) -> Path:
        # Combine the data into a single file
        if self.decompressed_files == []:
            raise ValueError("No decompressed files found. Run decompress_data first")

        combined_data: list[dict] = []
        for row in self._read_raw_data():
            # Strip DynamoDB type markers from row
            item = json_util.loads(row)
            # Extract table data from the Item key
            combined_data.append(item["Item"])

        if self.export_metadata is None:
            raise ValueError("No local export metadata found")

        combined_data_path = self.export_metadata.local_data_dir / "combined_data.json"
        log.debug("Writing combined data to file", file=combined_data_path)

        with combined_data_path.open("wb") as f:
            f.write(orjson.dumps(combined_data, option=orjson.OPT_APPEND_NEWLINE))
        return combined_data_path


class DataTransformer:
    def __init__(self, combined_json_data: Path) -> None:
        self.combined_data = combined_json_data

    def to_parquet(self, output_path: Path | None = None) -> Path:
        if output_path:
            parquet_path = output_path
        else:
            parquet_path = self.combined_data.with_suffix(".parquet")
        rel = duckdb.read_json(self.combined_data.as_posix())
        rel.to_parquet(parquet_path.as_posix())
        return parquet_path

    def to_csv(self, output_path: Path | None = None) -> Path:
        if output_path:
            csv_path = output_path
        else:
            csv_path = self.combined_data.with_suffix(".csv")
        rel = duckdb.read_json(self.combined_data.as_posix())
        rel.to_csv(csv_path.as_posix())
        return csv_path
