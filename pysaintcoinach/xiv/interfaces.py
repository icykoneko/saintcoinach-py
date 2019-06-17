from abc import abstractmethod


class ILocation(object):
    """
    Interface for objects defining a location in a zone (in map-coordinates).
    """

    @property
    @abstractmethod
    def map_x(self) -> float:
        pass

    @property
    @abstractmethod
    def map_y(self) -> float:
        pass

    @property
    @abstractmethod
    def place_name(self) -> 'PlaceName':
        pass
