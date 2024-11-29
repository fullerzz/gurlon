import pytest
from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from gurlon.squeal.creator import _tranform_pydantic_to_sqlmodel


class PydanticModel(BaseModel):
    id: int
    name: str
    age: int


class SQLModelInstance(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int


@pytest.fixture
def pydantic_model() -> PydanticModel:
    return PydanticModel(id=1, name="John Doe", age=30)


def test_tranform_pydantic_to_sqlmodel(pydantic_model: PydanticModel) -> None:
    resp = _tranform_pydantic_to_sqlmodel(pydantic_model)
    assert True
