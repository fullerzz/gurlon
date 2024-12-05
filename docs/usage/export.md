# Export Data from DynamoDB to S3

In order to eventually run SQL queries on your DynamoDB table data, it _first_ needs to be exported to S3.

!!! warning "PITR Must be Enabled"
    Your DynamoDB table needs to have [point-in-time recovery](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery_Howitworks.html) enabled in order to perform [ExportTableToPointInTime](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_ExportTableToPointInTime.html) operations.

## Create a `DataExporter`

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

## Export Data to S3 Bucket

Call the `export_data` function to begin [exporting your table data to S3](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport.HowItWorks.html).

If the operation succeeds, the export ARN will be returned.

```python
from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
export_arn = exporter.export_data()
```
