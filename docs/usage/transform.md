# Transform the Data to Different File Types

```python
from gurlon.processor import DataExporter

transformer = DataTransformer(combined_data)
parquet = transformer.to_parquet()
csv = transformer.to_csv()
duckdb = transformer.to_duckdb()
```

## SQLite Table

```python
from sqlmodel import Field, SQLModel

from gurlon.processor import DataTransformer


class TableItemModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    user_name: str
    email: str
    role: str
    full_name: str

transformer = DataTransformer(combined_data)
sql = transformer.to_sqlmodel(TableItemModel)
```
