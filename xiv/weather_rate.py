from typing import Iterable, List, Tuple, cast

from xiv import register_xivrow, XivRow, IXivSheet
from ex.relational import IRelationalRow

from xiv.weather import Weather


class WeatherRate(XivRow):
    @property
    def possible_weathers(self) -> Iterable[Weather]:
        return self._possible_weathers

    @property
    def weather_rates(self) -> Iterable[Tuple[int, Weather]]:
        return self._weather_rates

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(WeatherRate, self).__init__(sheet, source_row)

        count = 8
        w = []  # type: List[Weather]
        wr = []  # type: List[Tuple[int, Weather]]
        min = 0
        for i in range(count):
            weather = cast(Weather, self[('Weather', i)])
            rate = self.as_int32('Rate', i)

            w += [weather]
            wr += [(min + rate, weather)]

            min += rate

        self._possible_weathers = list(set(w))
        self._weather_rates = wr

register_xivrow(WeatherRate)
