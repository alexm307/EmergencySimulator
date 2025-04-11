import uuid

from sqlmodel import (
    Field,
    SQLModel
)

class BaseSQLModel(SQLModel):
    """By default, SQLModel classes with table=True does not validate member types.

    https://github.com/fastapi/sqlmodel/issues/52

    We can force it to validate by enabling a flag in the config:
    https://github.com/fastapi/sqlmodel/issues/52#issuecomment-1225746421
    """

    class Config:
        validate_assignment = True


class Location(BaseSQLModel, table=True):
    __tablename__ = "locations"

    location_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    county: str
    city: str
    latitude: float
    longitude: float
    medical: int
    fire: int
    police: int