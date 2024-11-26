from gurlon import processor


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
