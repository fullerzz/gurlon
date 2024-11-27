from gurlon.processor import DataExporter


def main() -> None:
    exporter = DataExporter("us-west-1", "gurlon-table", "gurlon-bucket")
    exporter.table_export_arn = (
        # ARN found in tests/data/mock_export_contents/gurlon/AWSDynamoDB/01732662110643-26e512e8/manifest-summary.json
        "arn:aws:dynamodb:us-west-1:863881196012:table/gurlon-table/export/01732662110643-26e512e8"
    )
    exporter.download_data()


if __name__ == "__main__":
    main()
