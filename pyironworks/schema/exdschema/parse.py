from abc import ABC, abstractmethod
from enum import Enum, IntEnum, auto
from dataclasses import dataclass, field, InitVar
from typing import Optional
import logging

import yaml

from .. import schema

@dataclass
class Sheet:
    name: str
    displayField: Optional[str] = None
    fields: list["Field"] = field(default_factory=list)
    relations: Optional[dict[list[str]]] = None


class FieldKind(Enum):
    Scalar = "scalar"
    Array = "array"
    Icon = "icon"
    ModelId = "modelId"
    Color = "color"
    Link = "link"


@dataclass
class Field:
    name: Optional[str] = None  # only optional for single-element arrays
    comment: Optional[str] = None

    type: InitVar["FieldKind"] = FieldKind.Scalar
    kind: "FieldKind" = field(init=False)

    count: Optional[int] = None
    fields: Optional[list["Field"]] = None

    condition: Optional["Condition"] = None
    targets: Optional[list[str]] = None

    relations: Optional[dict[list[str]]] = None

    def __post_init__(self, type):
        self.kind = FieldKind(type)


@dataclass
class Condition:
    switch: str
    cases: dict[int, list[str]]


def parse(data: str) -> schema.Sheet:
    try:
        sheet = yaml.safe_load(data)
        return map_sheet(Sheet(**sheet))
    except yaml.error.YAMLError:
        logging.exception("Failed to parse schema definition")
        raise


def map_sheet(sheet: Sheet) -> schema.Sheet:
    return schema.Sheet(
        name=sheet.name,
        order=schema.Order.Offset,
        node=map_struct([Field(**x) for x in sheet.fields]))


def map_struct(fields: list[Field]) -> schema.Node:
    struct_fields: list[schema.StructField] = []
    offset: int = 0

    for field in fields:
        name = field.name
        if not name:
            raise ValueError("Struct fields must have names")
        node = map_field(field)
        this_offset = offset
        offset += node.size()

        struct_fields.append(schema.StructField(
            offset=this_offset,
            name=name,
            node=node))

    return schema.Struct(struct_fields)


def map_field(field: Field) -> schema.Node:
    match field.kind:
        # Scalar columns
        case FieldKind.Scalar:
            return schema.Scalar(schema.Default())
        case FieldKind.Icon:
            return schema.Scalar(schema.Icon())
        case FieldKind.ModelId:
            return schema.Scalar(schema.Model())
        case FieldKind.Color:
            return schema.Scalar(schema.Color())
        
        # Arrays
        case FieldKind.Array if field.count is not None:
            if not field.fields:
                node = schema.Scalar(schema.Default())
            else:
                if len(field.fields) > 1:
                    node = map_struct([Field(**x) for x in field.fields])
                else:
                    node = map_field(Field(**field.fields[0]))

            return schema.Array(
                count=field.count,
                node=node)
        
        # Unconditional links
        case FieldKind.Link if field.condition is None and field.targets is not None:
            return schema.Scalar(schema.Reference(
                [schema.ReferenceTarget(sheet=target, selector=None, condition=None)
                 for target in field.targets]))
        
        # Conditional links
        case FieldKind.Link if field.condition is not None and field.targets is None:
            condition = Condition(**field.condition)
            targets = [
                schema.ReferenceTarget(
                    sheet=sheet,
                    selector=None,
                    condition=schema.ReferenceCondition(
                        selector=condition.switch,
                        value=value))
                for value, sheets in condition.cases.items()
                for sheet in sheets
            ]
            return schema.Scalar(schema.Reference(targets))
        
        case _:
            raise SyntaxError("Invalid EXDSchema field declaration: %r" % field)
