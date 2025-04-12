from collections.abc import Sequence

from sqlalchemy.exc import (
    NoResultFound,
)
from sqlmodel import (
    Session,
    select,
)

from exceptions import LocationNotFoundException
from config import get_database_engine

from .models import (
    Location,
    LocationBase,
)


class LocationsDataAccessLayer:
    def __init__(self) -> None:
        self._engine = get_database_engine()

    def list_locations(
        self
    ) -> Sequence[Location]:
        statement = select(Location)
        with Session(self._engine) as session:
            return session.exec(statement).fetchall()

    def get_location(
        self,
        city: str | None = None,
        county: str | None = None,
    ) -> Location:
        statement = select(Location)
        
        if city:
            statement = statement.where(Location.city == city)

        if county:
            statement = statement.where(Location.county == county)

        with Session(self._engine) as session:
            try:
                return session.exec(statement).one()
            except NoResultFound:
                raise LocationNotFoundException

    def create_location(
        self,
        location_base: LocationBase,
    ) -> Location:
        location = Location(
            **location_base.model_dump(),
        )
        with Session(self._engine) as session:
            session.add(location)
            session.commit()
            session.refresh(location)
            return location