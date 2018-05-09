from abc import ABC, abstractmethod
from ex.relational import IRelationalRow
from xiv import register_xivrow, XivRow, IXivSheet

from xiv.placename import PlaceName

class TerritoryType(XivRow):
    _weather_groups = None

    @property
    def name(self): return self.as_string('Name')
    @property
    def bg(self): return self.as_string('Bg')
    @property
    def map(self): return self['Map']
    @property
    def place_name(self): return self.as_T(PlaceName, 'PlaceName')
    @property
    def region_place_name(self): return self.as_T(PlaceName, 'PlaceName{Region}')
    @property
    def zone_place_name(self): return self.as_T(PlaceName, 'PlaceName{Zone}')
    @property
    def weather_rate(self):
        if self._weather_rate is not None:
            return self._weather_rate
        if self._weather_groups is None:
            self._weather_groups = self._build_weather_groups()

        rate_key = self.as_int32('WeatherRate')
        self._weather_rate = self._weather_groups.get(rate_key)
        if self._weather_rate is None:
            self._weather_rate = self.sheet.collection.get_sheet('WeatherRate')[rate_key]
        return self._weather_rate

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(TerritoryType, self).__init__(sheet, source_row)
        self._weather_rate = None

    def _build_weather_groups(self):
        _map = {}
        for weather_group in self.sheet.collection.get_sheet('WeatherGroup'):
            if weather_group.key != 0:
                continue

            _map[weather_group.parent_row.key] = weather_group['WeatherRate']
        return _map


register_xivrow(TerritoryType)
