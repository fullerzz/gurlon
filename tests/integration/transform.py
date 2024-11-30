import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from sqlmodel import Field, SQLModel

from gurlon.processor import DataTransformer


class UserSqlModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    user_name: str
    email: str
    role: str
    full_name: str


def log_output(parquet: Path, csv: Path, sql: Path) -> None:
    outputs = {
        "Parquet": parquet.as_posix(),
        "CSV": csv.as_posix(),
        "SQLite": sql.as_posix(),
    }
    syntax = Syntax(json.dumps(outputs, indent=2), "json", theme="lightbulb")
    console = Console()
    panel = Panel(syntax, title="[bold cyan]Data Transformation Output[/]", expand=False)
    console.print(panel)


def main() -> None:
    combined_data = Path.home() / "Downloads" / "dynamodb_exports" / "combined_data.json"
    if not combined_data.exists():
        raise FileNotFoundError(f"File not found: {combined_data}")
    transformer = DataTransformer(combined_data)
    parquet = transformer.to_parquet()
    csv = transformer.to_csv()
    sql = transformer.to_sqlmodel(UserSqlModel)
    log_output(parquet, csv, sql)


if __name__ == "__main__":
    main()
