from ex.excollection import ExCollection
from ex.relational.datasheet import RelationalDataSheet
from ex.relational.definition import RelationDefinition
from ex.relational import IRelationalRow, IRelationalSheet
from ex.relational.header import RelationalHeader
from ex.relational.multisheet import RelationalMultiSheet, RelationalMultiRow


class RelationalExCollection(ExCollection):
    @property
    def definition(self) -> RelationDefinition: return self.__definition

    @definition.setter
    def definition(self, value): self.__definition = value

    def __init__(self, pack_collection):
        super(RelationalExCollection, self).__init__(pack_collection)
        self.__definition = RelationDefinition()

    def _create_header(self, name, file):
        return RelationalHeader(self, name, file)

    def _create_sheet(self, header):
        from ex import variant1 as Variant1
        from ex import variant2 as Variant2
        rel_header = header  # type: RelationalHeader
        if rel_header.variant == 2:
            return self.__create_sheet(Variant2.RelationalDataRow, rel_header)
        return self.__create_sheet(Variant1.RelationalDataRow, rel_header)

    def __create_sheet(self, t, header):
        if header.available_languages_count >= 1:
            return RelationalMultiSheet[RelationalMultiRow, t](RelationalMultiRow,
                                                               t, self, header)
        return RelationalDataSheet[t](t, self, header, header.available_languages[0])

    def get_sheet(self, id_or_name) -> IRelationalSheet:
        return super(RelationalExCollection, self).get_sheet(id_or_name)

    def find_reference(self, key: int) -> IRelationalRow:
        for sheet_def in filter(lambda d: d.is_generic_reference_target,
                                self.definition.sheet_definitions):
            sheet = self.get_sheet(sheet_def.name)
            if not any(filter(lambda r: key in r, sheet.header.data_file_ranges)):
                continue

            if key not in sheet:
                continue

            return sheet[key]

        return None
