from typing import Type

from .xivcollection import XivCollection
from .sheet import IXivRow, IXivSheet, XivRow, XivSheet


REGISTERED_ROW_CLASSES = {}


def register_xivrow(cls: Type):
    REGISTERED_ROW_CLASSES[cls.__name__] = cls


def as_row_type(sheet_name: str) -> Type:
    return REGISTERED_ROW_CLASSES.get(sheet_name, XivRow)


# Import sheet-specific classes
from .item import Item
from .placename import PlaceName
from .territory_type import TerritoryType
from .weather import Weather
from .weather_rate import WeatherRate
