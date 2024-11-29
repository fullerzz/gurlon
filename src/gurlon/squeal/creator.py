from pathlib import Path

from pydantic import BaseModel
from sqlmodel import SQLModel

from gurlon.squeal.models import TableModel


def create_sqlite_table(model: BaseModel, db_path: Path) -> None:
    return None


def _tranform_pydantic_to_sqlmodel(model: BaseModel) -> SQLModel:
    target = TableModel()
    for field_name in model.model_fields:
        # TODO: Figure out how to add attribute to already created model
        target.__setattr__(field_name, target.__getattribute__(field_name))
    return target
