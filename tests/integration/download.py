from pathlib import Path

from gurlon.processor import DataExporter


def main() -> None:
    exporter = DataExporter(
        "us-west-1",
        "gurlon-table",
        "gurlon-bucket",
        "arn:aws:dynamodb:us-west-1:863881196012:table/gurlon-table/export/01732662110643-26e512e8",
    )
    download_dir = Path.home() / "Downloads" / "dynamodb_exports"
    exporter.download_data(download_dir=download_dir)


if __name__ == "__main__":
    main()
