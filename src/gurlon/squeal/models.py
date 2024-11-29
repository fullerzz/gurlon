from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

T = TypeVar("T")


class InputModel(BaseModel, Generic[T]):
    content: T


class TableModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
