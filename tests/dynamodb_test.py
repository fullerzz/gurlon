from gurlon import dynamodb


def test_create_dynamodb_table_instance(dynamodb_table: str) -> None:
    table = dynamodb.DynamoTable(table_name=dynamodb_table)
    assert table.table_name == dynamodb_table
    assert table.metadata is not None
    assert table.metadata.primary_key == "user_id"
