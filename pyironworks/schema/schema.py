from abc import ABC, abstractmethod
from enum import Enum, IntEnum, auto
from dataclasses import dataclass, field
from typing import Optional

class Schema(ABC):

    @abstractmethod
    def sheet(self, name: str) -> "Sheet":
        """Get the schema for the specified sheet"""
        ...


class Order(IntEnum):
    Index = auto()
    Offset = auto()


@dataclass
class Sheet:
    """Schema and metadata for a sheet within an Excel database."""

    name: str
    order: Order
    node: "Node"



class Node:
    def size(self) -> int:
        """The size of a given node, in columns."""
        raise NotImplementedError


@dataclass
class Array(Node):
    count: int
    node: Node

    def size(self) -> int:
        return self.count * self.node.size()


@dataclass
class Scalar(Node):
    scalar: "ScalarKind"

    def size(self) -> int:
        return 1


@dataclass
class Struct(Node):
    fields: list["StructField"] = field(default_factory=list)

    def size(self) -> int:
        if not self.fields:
            return 0
        last_field = self.fields[-1]
        return last_field.offset + last_field.node.size()


class ScalarKind:
    pass


@dataclass
class Default(ScalarKind):
    pass


@dataclass
class Reference(ScalarKind):
    targets: list["ReferenceTarget"]


@dataclass
class Icon(ScalarKind):
    pass


@dataclass
class Model(ScalarKind):
    pass


@dataclass
class Color(ScalarKind):
    pass


@dataclass
class ReferenceTarget:
    sheet: str
    selector: Optional[str] = None
    condition: Optional["ReferenceCondition"] = None


@dataclass
class ReferenceCondition:
    selector: str
    value: int


@dataclass
class StructField:
    offset: int
    name: str
    node: Node