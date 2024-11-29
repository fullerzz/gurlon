from pathlib import Path

from gurlon import processor
from tests.conftest import MOCK_EXPORT_ARN


def test_create_data_exporter_instance(populated_table: str, s3_bucket: str) -> None:
    exporter = processor.DataExporter(aws_region="us-east-1", table_name=populated_table, bucket_name=s3_bucket)
    assert exporter.aws_region == "us-east-1"
    assert exporter.table.table_name == populated_table
    assert exporter.bucket.bucket_name == s3_bucket


def test_export_to_s3(populated_table: str, s3_bucket: str) -> None:
    exporter = processor.DataExporter(aws_region="us-east-1", table_name=populated_table, bucket_name=s3_bucket)
    export_arn = exporter.export_data()
    assert export_arn is not None
    assert export_arn.startswith("arn:aws:dynamodb:")


def test_export_and_download(populated_table: str, populated_bucket: str, tmp_path: Path) -> None:
    exporter = processor.DataExporter(aws_region="us-east-1", table_name=populated_table, bucket_name=populated_bucket)
    export_arn = exporter.export_data()
    assert export_arn is not None
    assert export_arn == MOCK_EXPORT_ARN
    download_dir = tmp_path / "dynamodb_exports"
    download_dir.mkdir()
    combined_path = exporter.download_data(download_dir)
    assert combined_path.exists() is True
    assert combined_path.is_file()
    assert combined_path.suffix == ".json"
    assert combined_path.stat().st_size > 0
    assert combined_path.parent.name == "dynamodb_exports"
    assert combined_path.name == "combined_data.json"
