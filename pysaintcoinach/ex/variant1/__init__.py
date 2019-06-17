from typing import Dict, Union
from struct import unpack_from

from ..datasheet import DataRowBase, IDataSheet
from ..relational.datasheet import IRelationalDataRow, IRelationalDataSheet


class DataRow(DataRowBase):
    METADATA_LENGTH = 0x06

    @property
    def length(self): return self.__length

    def __init__(self, sheet: IDataSheet, key: int, offset: int):
        super(DataRow, self).__init__(sheet, key, offset + self.METADATA_LENGTH)

        b = sheet.get_buffer()
        if len(b) < (offset + self.METADATA_LENGTH):
            raise ValueError("Index out of range")

        self.__length, c = unpack_from(">lh", b, offset)
        if c != 1:
            raise ValueError("Invalid data")


class RelationalDataRow(DataRow, IRelationalDataRow):
    def __init__(self,
                 sheet: IDataSheet,
                 key: int,
                 offset: int):
        super(RelationalDataRow, self).__init__(sheet, key, offset)
        self.__value_references = {}  # type: Dict[str, object]

    @property
    def sheet(self) -> IRelationalDataSheet:
        return super(RelationalDataRow, self).sheet

    def __str__(self):
        def_col = self.sheet.header.default_column
        if def_col is not None:
            return "%s" % self[def_col.index]
        else:
            return "%s#%u" % (self.sheet.header.name, self.key)

    @property
    def default_value(self) -> object:
        def_col = self.sheet.header.default_column
        return self[def_col.index] if def_col is not None else None

    def __getitem__(self, item: str) -> object:
        if isinstance(item, int):
            return super(RelationalDataRow, self).__getitem__(item)

        val = self.__value_references.get(item)
        if val is not None:
            return val

        col = self.sheet.header.find_column(item)
        if col is None:
            raise KeyError(item)
        val = self[col.index]

        self.__value_references[item] = val
        return val

    def get_raw(self, column_name: Union[str, int] = None, **kwargs) -> object:
        if 'column_index' in kwargs:
            return super(RelationalDataRow, self).get_raw(**kwargs)
        if isinstance(column_name, int):
            return super(RelationalDataRow, self).get_raw(column_name)

        column = self.sheet.header.find_column(column_name)
        if column is None:
            raise KeyError(column_name)
        return column.read_raw(self.sheet.get_buffer(), self)
