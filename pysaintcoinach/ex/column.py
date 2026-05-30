import struct
import io

from .datareaders import DataReader
from .. import ex


class Column(object):
    """
    Class for representing columns inside EX files.
    """

    def __init__(self, header: 'ex.Header', column_based_index: int, buffer: bytes, offset: int):
        TYPE_OFFSET = 0x00
        POSITION_OFFSET = 0x02

        self.__header = header
        self.__column_based_index = column_based_index
        self.__type, = struct.unpack('>H', buffer[offset + TYPE_OFFSET:][:2])
        self.__offset, = struct.unpack('>H', buffer[offset + POSITION_OFFSET:][:2])
        self.__reader = DataReader.get_reader(self.type)

    @property
    def header(self) -> 'ex.Header':
        """
        Gets the Header of the EX file the column is in.
        """
        return self.__header

    @property
    def column_based_index(self) -> int:
        """
        Gets the index of the column inside the EX file.
        """
        return self.__column_based_index

    @property
    def offset_based_index(self) -> int:
        """
        Gets the index of the column based on offset position
        """
        return self.__offset_based_index

    @offset_based_index.setter
    def offset_based_index(self, value: int):
        self.__offset_based_index = value

    @property
    def type(self) -> int:
        """
        Gets the integer identifier for the type of the column's data.
        """
        return self.__type

    @property
    def offset(self) -> int:
        """
        Gets the position of the column's data in a row.
        """
        return self.__offset

    @property
    def reader(self) -> DataReader:
        """
        Gets the DataReader used to read column's data.
        """
        return self.__reader

    @property
    def value_type(self) -> str:
        return self.reader.name

    def read(self, buffer: bytes, row: 'ex.IDataRow', offset: int = None):
        return self.read_raw(buffer, row, offset)

    def read_raw(self, buffer: bytes, row: 'ex.IDataRow', offset: int = None):
        if offset is None:
            return self.reader.read(buffer, col=self, row=row)
        else:
            return self.reader.read(buffer, offset=offset)
