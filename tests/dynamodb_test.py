from gurlon import dynamodb


def test_create_dynamodb_table_instance(populated_table: str) -> None:
    table = dynamodb.DynamoTable(table_name=populated_table)
    assert table.table_name == populated_table
    assert table.metadata is not None
    assert table.metadata.primary_key == "user_id"
    assert table.metadata.total_items > 0


def test_export_to_s3(populated_table: str, s3_bucket: str) -> None:
    table = dynamodb.DynamoTable(table_name=populated_table)
    export_arn = table.export_to_s3(bucket=s3_bucket, key_prefix="gurlon")
    assert export_arn is not None
    assert export_arn.startswith("arn:aws:dynamodb:")
