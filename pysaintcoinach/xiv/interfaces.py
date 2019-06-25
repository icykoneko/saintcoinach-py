from abc import abstractmethod
from typing import Iterable


class IItemSource(object):
    """
    Interface for objects from which `Item`s can be obtained.
    """

    @property
    @abstractmethod
    def items(self) -> 'Iterable[Item]':
        """
        Gets the `Item`s that can be obtained from the current object.
        :return: The `Item`s that can be obtained from the current object.
        """
        pass


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


class ILocatable(object):
    """
    Interface for objects that have specific locations.
    """

    @property
    @abstractmethod
    def locations(self) -> Iterable[ILocation]:
        """
        Gets the locations of the current object.
        :return: The locations of the current object.
        """
        pass
