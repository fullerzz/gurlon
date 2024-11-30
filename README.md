# gurlon

## Overview

`gurlon` is a library designed to make the process of exporting data from Dynamo to your local filesystem easier.

There are 3 main steps to the `gurlon` export process:

1. Instantiate a new `DataExporter` and invoke `export_data` to begin a DynamoDB PointInTimeExport to S3
2. Call the `DataExporter` function `download_data` once the DynamoDB export is complete to combine the exported data into a single json file on your local filesystem
3. Transform your local copy of the exported table data into another storage format: `csv`, `parquet`

## Usage

### Export Data from DynamoDB to S3

```python
from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
export_arn = exporter.export_data()
print(f"Export ARN: {export_arn}")
```

### Download Exported Data

```python
from pathlib import Path

from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
download_dir = Path.home() / "Downloads" / "dynamodb_exports"
exporter.download_data(download_dir=download_dir)
```

### Transform the Data to Different File Types

```python
from gurlon.processor import DataExporter

transformer = DataTransformer(combined_data)
parquet = transformer.to_parquet()
csv = transformer.to_csv()
duckdb = transformer.to_duckdb()
```

#### SQLite Table

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
