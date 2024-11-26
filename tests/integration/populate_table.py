import boto3
from infra import REGION, TABLE_NAME  # type: ignore[import-not-found]
from pydantic import BaseModel


class TableItem(BaseModel):
    user_id: str
    user_name: str
    email: str
    role: str
    full_name: str


def generate_table_items() -> list[TableItem]:
    items: list[TableItem] = []
    for i in range(100):
        if i % 2 == 0:
            role = "admin"
            full_name = "Bob Smith"
        else:
            role = "user"
            full_name = "Alice Doe"
        item = TableItem(
            user_id=f"user_{i}", user_name=f"user_{i}", email=f"user_{i}@gmail.com", role=role, full_name=full_name
        )
        items.append(item)
    return items


def populate_table() -> None:
    session = boto3.Session(region_name=REGION)
    table = session.resource("dynamodb").Table(TABLE_NAME)
    for item in generate_table_items():
        table.put_item(Item=item.model_dump())


if __name__ == "__main__":
    populate_table()
