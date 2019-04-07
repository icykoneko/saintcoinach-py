from typing import Dict, Generic

from ex.relational.excollection import RelationalExCollection
from ex.relational.sheet import IRelationalSheet
from pack import PackCollection
from xiv.sheet import XivSheet, XivRow, XivSheet2, XivSubRow


class XivCollection(RelationalExCollection):
    def __init__(self, pack_collection: PackCollection):
        super(XivCollection, self).__init__(pack_collection)
        self.__sheet_name_to_type_map = {}  # type: Dict[str, type]

    def _create_sheet(self, header):
        base_sheet = super(XivCollection, self)._create_sheet(header)
        xiv_sheet = self._create_xiv_sheet(base_sheet)
        if xiv_sheet is not None:
            return xiv_sheet
        if header.variant == 2:
            return XivSheet2[XivSubRow](XivSubRow, self, base_sheet)
        return XivSheet[XivRow](XivRow, self, base_sheet)

    def _create_xiv_sheet(self, source_sheet: IRelationalSheet):
        match = self.__get_xiv_row_type(source_sheet.name)
        if match is None:
            return None

        if source_sheet.header.variant == 2:
            return XivSheet2[match](match, self, source_sheet)
        return XivSheet[match](match, self, source_sheet)

    def __get_xiv_row_type(self, sheet_name: str):
        import xiv
        if sheet_name in xiv.__dict__:
            return xiv.__dict__[sheet_name]
        return None
