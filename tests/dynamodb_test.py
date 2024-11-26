from gurlon import dynamodb


def test_create_dynamodb_table_instance(populated_table: str) -> None:
    table = dynamodb.DynamoTable(table_name=populated_table)
    assert table.table_name == populated_table
    assert table.metadata is not None
    assert table.metadata.primary_key == "user_id"
    assert table.metadata.total_items > 0
