from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional

import yaml


class FieldType(str, Enum):
    Scalar = "scalar"
    Array = "array"
    Icon = "icon"
    ModelId = "modelId"
    Color = "color"
    Link = "link"


@dataclass
class Condition:
    switch: Optional[str] = None
    cases: Optional[dict[int, list[str]]] = None

    @staticmethod
    def from_dict(data: dict) -> "Condition":
        raw_cases = data.get("cases")
        cases = None
        if raw_cases is not None:
            cases = {int(k): v for k, v in raw_cases.items()}
        return Condition(
            switch=data.get("switch"),
            cases=cases
        )


@dataclass
class Field:
    # Runtime-assigned, not serialized
    index: int = field(default=0, repr=False)
    field_count: int = field(default=0, repr=False)

    name: Optional[str] = None
    count: Optional[int] = None
    type: FieldType = FieldType.Scalar
    comment: Optional[str] = None
    fields: Optional[list["Field"]] = None
    condition: Optional[Condition] = None
    targets: Optional[list[str]] = None

    @staticmethod
    def from_dict(data: dict) -> "Field":
        raw_type = data.get("type", "scalar")
        try:
            field_type = FieldType(raw_type)
        except ValueError:
            field_type = FieldType.Scalar

        nested_fields = None
        if data.get("fields"):
            nested_fields = [Field.from_dict(f) for f in data["fields"]]

        condition = None
        if data.get("condition"):
            condition = Condition.from_dict(data["condition"])

        return Field(
            name=data.get("name"),
            count=data.get("count"),
            type=field_type,
            comment=data.get("comment"),
            fields=nested_fields,
            condition=condition,
            targets=data.get("targets"),
        )


@dataclass
class Sheet:
    name: str = ""
    display_field: Optional[str] = None
    fields: list[Field] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict) -> "Sheet":
        return Sheet(
            name=data.get("name", ""),
            display_field=data.get("displayField"),
            fields=[Field.from_dict(f) for f in data.get("fields", [])],
        )

    @staticmethod
    def from_yaml(text: str) -> "Sheet":
        data = yaml.safe_load(text)
        return Sheet.from_dict(data)

    @staticmethod
    def from_yaml_file(path: str) -> "Sheet":
        with open(path, "r", encoding="utf-8") as fh:
            return Sheet.from_yaml(fh.read())
