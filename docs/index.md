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
