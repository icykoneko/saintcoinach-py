import json

from ex.relational.definition import ViewDefinition


class ViewCollection(object):
    def __init__(self, view_definitions_by_sheet_name):
        self._view_definitions_by_sheet_name = view_definitions_by_sheet_name

    @staticmethod
    def from_json(str_or_obj) -> 'ViewCollection':
        if isinstance(str_or_obj, str):
            str_or_obj = json.loads(str_or_obj)
        return ViewCollection(dict([(v.sheet_name, v) for v in
                                    [ViewDefinition.from_json(x) for x in str_or_obj['views']]]))