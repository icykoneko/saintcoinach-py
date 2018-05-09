import typing

from ex.relational.sheet import IRelationalRow
from xiv.sheet import XivRow, XivSheet


class XivSheetMeta(typing.GenericMeta):

    def __new__(cls, name, bases, namespace, *args, **kwargs):
        self = super().__new__(cls, name, bases, namespace, *args, **kwargs)
        if 'args' in kwargs:
            self._row_cls, = kwargs['args']
        return self

T = typing.TypeVar('T')


class XivRowT(XivRow):
    def __new__(cls, sheet, source_row):
        self = cls.__init__(sheet, source_row)
        return self

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XivSheetT(XivSheet[T], metaclass=XivSheetMeta):
    def __new__(cls, *args, **kwargs):
        #kwargs['row_cls'], = cls._sheet_name
        row_cls = cls._row_cls
        if row_cls is not None:
            self = super().__new__(cls, row_cls, *args, **kwargs)
        else:
            self = super().__new__(cls, XivRow, *args, **kwargs)
        return self

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


