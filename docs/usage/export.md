# Export Data from DynamoDB to S3

```python
from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
export_arn = exporter.export_data()
print(f"Export ARN: {export_arn}")
```
