from collections.abc import Sequence
from typing import Annotated
from uuid import UUID


from sqlalchemy import (
    Engine,
    func,
)
from sqlalchemy.exc import (
    IntegrityError,
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

    # def update_location(
    #     self,
    #     location_id: UUID,
    #     site_id: UUID,
    #     location_request: LocationBase,
    #     new_site: UUID | None,
    # ) -> Location:
    #     statement = select(Location).where(Location.site_id == site_id).where(Location.location_id == location_id)
    #     with Session(self._engine) as session:
    #         results = session.exec(statement)
    #         try:
    #             db_location = results.one()
    #         except NoResultFound:
    #             raise LocationNotFoundException

    #         old_meter = session.exec(
    #             select(Meter).where(Meter.meter_id == db_location.meter_id),
    #         ).first()

    #         db_location.sqlmodel_update(location_request.model_dump())
    #         if new_site:
    #             db_location.site_id = new_site
    #         session.commit()

    #         meter = session.exec(
    #             select(Meter).where(Meter.meter_id == db_location.meter_id),
    #         ).first()

    #         if meter and old_meter:
    #             meter.measuring = db_location.display_name
    #             meter.measuring_type = MeterMeasuringType.location

    #             old_meter.measuring = None
    #             old_meter.measuring_type = None

    #             session.add(meter)
    #             session.add(old_meter)
    #             session.commit()
    #             session.refresh(meter)
    #             session.refresh(old_meter)
    #             session.refresh(db_location)
    #         else:
    #             raise MeterNotFoundException

    #         return db_location

    # def delete_location(self, location_id: UUID, site_id: UUID) -> None:
    #     statement = select(location).where(location.site_id == site_id).where(location.location_id == location_id)
    #     with Session(self._engine) as session:
    #         try:
    #             db_location = session.exec(statement).one()
    #         except NoResultFound:
    #             raise LocationNotFoundException
    #         session.delete(db_location)
    #         session.commit()
