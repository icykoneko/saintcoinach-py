from typing import Optional

from .schema import Field, FieldType, Sheet


def flatten(sheet: Sheet) -> Sheet:
    fields: list[Field] = []
    for field in sheet.fields:
        _emit(fields, field)

    sheet.fields = fields
    for i in range(len(sheet.fields)):
        sheet.fields[i].index = i

    return sheet


def _emit(fields: list[Field], field: Field, hierarchy: Optional[list[str]] = None) -> None:
    if field.type != FieldType.Array:
        # Single Field
        fields.append(_create_field(field, False, 0, hierarchy))
    elif field.type == FieldType.Array:
        # We can have an array without fields, it's just scalars in this case.
        if field.fields is None:
            for i in range(field.count):
                fields.append(_create_field(field, True, i, hierarchy))
        else:
            for i in range(field.count):
                for nested_field in field.fields:
                    usable_hierarchy = [] if hierarchy is None else list(hierarchy)
                    usable_hierarchy.append(f"{field.name}[{i}]")
                    _emit(fields, nested_field, usable_hierarchy)


def _create_field(base_field: Field, field_is_array_element: bool, index: int, hierarchy: list[str]) -> Field:
    added_field = Field(
        comment=base_field.comment,
        count=None,
        type=FieldType.Scalar if base_field.type == FieldType.Array else base_field.type,
        fields=None,
        condition=base_field.condition,
        targets=base_field.targets)

    name = f"{base_field.name}"

    if field_is_array_element:
        name = f"{name}[{index}]"

    if hierarchy is not None:
        added_field.name = '.'.join(hierarchy)
        if name:
            added_field.name += f".{name}"
    else:
        added_field.name = name

    return added_field


def _strip_array_indices(name: str) -> str:
    index = name.find('[')
    return name if index == -1 else name[:index]