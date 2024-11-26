from gurlon.processor import DataExporter


def main() -> None:
    exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
    export_arn = exporter.export_data()
    print(f"Export ARN: {export_arn}")


if __name__ == "__main__":
    main()
