from pathlib import Path

import pytest
from sqlmodel import Field, SQLModel

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


@pytest.fixture
def combined_data() -> bytes:
    with Path("tests/data/expected/combined_data.json").open("rb") as input:
        return input.read()


@pytest.fixture
def combined_data_path(tmp_path: Path, combined_data: bytes) -> Path:
    data_path = tmp_path / "combined_data.json"
    with data_path.open("wb") as output:
        output.write(combined_data)
    return data_path


def test_transform_data_csv(combined_data_path: Path, tmp_path: Path) -> None:
    transformer = processor.DataTransformer(combined_data_path)
    output_path = tmp_path / "transformed_data.csv"
    csv_path = transformer.to_csv(output_path)
    assert csv_path.exists() is True
    assert csv_path.is_file()
    assert csv_path.suffix == ".csv"
    assert csv_path.stat().st_size > 0
    assert output_path == csv_path


def test_transform_data_parquet(combined_data_path: Path, tmp_path: Path) -> None:
    transformer = processor.DataTransformer(combined_data_path)
    output_path = tmp_path / "transformed_data.parquet"
    parquet_path = transformer.to_csv(output_path)
    assert parquet_path.exists() is True
    assert parquet_path.is_file()
    assert parquet_path.suffix == ".parquet"
    assert parquet_path.stat().st_size > 0
    assert output_path == parquet_path


def test_transform_data_sqlmodel(combined_data_path: Path, tmp_path: Path) -> None:
    class UserSqlModel(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        user_id: str
        user_name: str
        email: str
        role: str
        full_name: str

    transformer = processor.DataTransformer(combined_data_path)
    output_path = tmp_path / "gurlon-sqlite.db"
    sqlite_path = transformer.to_sqlmodel(UserSqlModel, output_path)
    assert sqlite_path.exists() is True
    assert sqlite_path.is_file()
    assert sqlite_path.suffix == ".db"
    assert sqlite_path.stat().st_size > 0
    assert output_path == sqlite_path


def test_transform_data_duckdb(combined_data_path: Path, tmp_path: Path) -> None:
    transformer = processor.DataTransformer(combined_data_path)
    output_path = tmp_path / "transformed_data.duckdb"
    duckdb_path = transformer.to_csv(output_path)
    assert duckdb_path.exists() is True
    assert duckdb_path.is_file()
    assert duckdb_path.suffix == ".duckdb"
    assert duckdb_path.stat().st_size > 0
    assert output_path == duckdb_path
