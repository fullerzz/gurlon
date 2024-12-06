# Gurlon Docs

## Overview

`gurlon` is a library designed to make the process of exporting data from Dynamo to your local filesystem easier.

!!! tip "Key Concepts"
    There are 3 main steps to the `gurlon` export process:

    1. Instantiate a new `DataExporter` and invoke `export_data` to begin a DynamoDB PointInTimeExport to S3
    2. Call the `DataExporter` function `download_data` once the DynamoDB export is complete to combine the exported data into a single json file on your local filesystem
    3. Transform your local copy of the exported table data into another storage format: `csv`, `parquet`

## Installation

=== "pip"

    ``` python
    pip install gurlon
    ```

=== "uv"

    ``` python
    uv add gurlon
    ```

## Export Data from DynamoDB to S3

In order to eventually run SQL queries on your DynamoDB table data, it _first_ needs to be exported to S3.

!!! warning "PITR Must be Enabled"
    Your DynamoDB table needs to have [point-in-time recovery](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery_Howitworks.html) enabled in order to perform [ExportTableToPointInTime](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_ExportTableToPointInTime.html) operations.

### Create a `DataExporter`

Import the `DataExporter` class into your Python file, and create a `DataExporter` instance by passing the following parameters:

- `aws_region: str`
- `table_name: str`
- `bucket_name: str`

```python
from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
```

### Provide AWS Credentials

Make sure the environment this code is executing in supplies your AWS credentials through either:

- Environment variables - [AWS Docs Reference](https://docs.aws.amazon.com/sdkref/latest/guide/environment-variables.html)
- The `~/.aws/config` file - [AWS Docs Reference](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)

??? tip "Additional Details on Authentication Process"

    Gurlon uses `boto3` to perform AWS operations, so you can read up more on the underlying authentication process [here](https://boto3.amazonaws.com/v1/documentation/api/1.35.9/guide/configuration.html#guide-configuration).

### Trigger the Export

Call the `export_data` function to begin [exporting your table data to S3](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport.HowItWorks.html).

If the operation succeeds, the export ARN will be returned.

```python
from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
export_arn = exporter.export_data()
```

## Download Exported Data

Once your table export to S3 is complete, you can download the data to your local filesystem.

```python
from pathlib import Path

from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
exporter.table_export_arn = "YOUR:TABLE:EXPORT:ARN"

download_dir = Path.home() / "Downloads" / "dynamodb_exports"
exporter.download_data(download_dir=download_dir)
```

### Output

Gurlon takes care of decompressing the exported data and combining it into a valid JSON file. This combined JSON file is stored inside the `download_dir` you specified previously.

## Transform the Data to Different File Types

!!! success
    Now that the exported data is present locally, you can begin to transform it into different formats.

### Create a `DataTransformer`

```python
from pathlib import Path

from gurlon.processor import DataTransformer

download_dir = Path.home() / "Downloads" / "dynamodb_exports"
combined_data = download_dir / "combined_data.json"
transformer = DataTransformer(combined_data)
```

### Parquet

```python
from pathlib import Path

from gurlon.processor import DataTransformer

download_dir = Path.home() / "Downloads" / "dynamodb_exports"
combined_data = download_dir / "combined_data.json"
transformer = DataTransformer(combined_data)

parquet = transformer.to_parquet()
```

### CSV

```python
from pathlib import Path

from gurlon.processor import DataTransformer

download_dir = Path.home() / "Downloads" / "dynamodb_exports"
combined_data = download_dir / "combined_data.json"
transformer = DataTransformer(combined_data)

csv = transformer.to_csv()
```

### DuckDB

```python
from pathlib import Path

from gurlon.processor import DataTransformer

download_dir = Path.home() / "Downloads" / "dynamodb_exports"
combined_data = download_dir / "combined_data.json"
transformer = DataTransformer(combined_data)

duckdb = transformer.to_duckdb()
```

### SQLite Table

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
