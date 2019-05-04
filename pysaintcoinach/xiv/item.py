from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet


class ItemBase(XivRow):
    @property
    def name(self):
        return self.get_raw('Name')

    @property
    def description(self):
        return self.get_raw('Description')

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(ItemBase, self).__init__(sheet, source_row)


@xivrow
class Item(ItemBase):
    @property
    def bid(self):
        return self.get_raw('Price{Low}')

    @property
    def ask(self):
        return self.get_raw('Price{Mid}')

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(Item, self).__init__(sheet, source_row)
