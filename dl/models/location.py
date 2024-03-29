from decimal import Decimal
from typing import Any

from sqlalchemy import Column, DECIMAL
from sqlalchemy.orm import validates

from dl.models.base_model import BaseModel, ModelException


class LocationModel(BaseModel):
    __tablename__ = 'location'

    latitude = Column(DECIMAL, nullable=False)
    longitude = Column(DECIMAL, nullable=False)

    @validates('latitude')
    def validate_latitude(self, _: Any, value: Decimal) -> Decimal:
        if Decimal(-90) <= value <= Decimal(90):
            return value
        raise ModelException('Number is not right')

    @validates('longitude')
    def validate_longitude(self, _: Any, value: Decimal) -> Decimal:
        if Decimal(-180) <= value <= Decimal(180):
            return value
        raise ModelException('Number is not right')
