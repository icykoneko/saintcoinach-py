from .ex.language import Language


class ExdHelper(object):
    from .ex import ISheet, IRow, IMultiRow
    @staticmethod
    def convert_rows(sheet: ISheet, language: Language = None, cols = None):
        if cols is None:
            cols = sheet.header.columns

        if sheet.header.variant == 1:
            return ExdHelper.convert_rows_core(sheet, language, cols, ExdHelper.get_row_key)
        else:
            return ExdHelper.convert_rows_core(sheet, language, cols, ExdHelper.get_sub_row_key)

    @staticmethod
    def convert_rows_core(rows, language, cols, get_key):
        out_rows = {}
        for row in sorted(rows, key=lambda x: x.key):
            key, row_dict = ExdHelper._convert_row(row, language, cols, get_key)
            out_rows[key] = row_dict
        return out_rows

    @staticmethod
    def convert_row(row: IRow, language: Language = None):
        cols = row.sheet.header.columns
        if row.sheet.header.variant == 1:
            get_key = ExdHelper.get_row_key
        else:
            get_key = ExdHelper.get_sub_row_key
        return ExdHelper._convert_row(row, language, cols, get_key)

    @staticmethod
    def _convert_row(row, language, cols, get_key):
        from .ex import ISheet, IRow, IMultiRow
        from .xiv import XivRow, IXivRow
        use_row = row

        if isinstance(use_row, IXivRow):
            use_row = row.source_row
        multi_row = use_row  # type: IMultiRow

        key = get_key(use_row)
        out_row = {}
        for col in cols:
            v = None
            if language is None or multi_row is None:
                v = use_row[col.index]
            else:
                v = multi_row[(col.index, language)]

            if v is not None:
                out_row[col.name or col.index] = str(v)

        return key, out_row

    @staticmethod
    def get_row_key(row: IRow):
        return row.key

    @staticmethod
    def get_sub_row_key(row: IRow):
        from .ex import variant2 as Variant2
        sub_row = row  # type: Variant2.SubRow
        return sub_row.full_key
