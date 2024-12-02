# Download Exported Data

```python
from pathlib import Path

from gurlon.processor import DataExporter

exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
download_dir = Path.home() / "Downloads" / "dynamodb_exports"
exporter.download_data(download_dir=download_dir)
```
