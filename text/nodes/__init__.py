from typing import TypeVar, Generic, Type, Union, Iterable, List
from abc import ABC, abstractmethod

from text.utils import TagType, NodeFlags, StringTokens
import text.expressions as expressions

T = TypeVar('T')


class INodeVisitor(Generic[T]):
    @abstractmethod
    def visit(self, node: Union['XivString', 'OpenTag', 'CloseTag', 'IfElement', 'GenericElement',
                                'EmptyElement', 'DefaultElement', 'Comparison', 'TopLevelParameter',
                                'SwitchElement', 'StaticString', 'StaticInteger', 'StaticByteArray',
                                'Parameter']) -> T:
        pass


class INode(ABC):
    @property
    @abstractmethod
    def tag(self) -> TagType: pass

    @property
    @abstractmethod
    def flags(self) -> NodeFlags: pass

    @abstractmethod
    def __str__(self): pass

    @abstractmethod
    def accept(self, visitor: INodeVisitor[T]) -> T: pass


class IExpressionNode(INode):
    @abstractmethod
    def evaluate(self, parameters: 'EvaluationParameters') -> expressions.IExpression:
        pass


class IConditionalNode(IExpressionNode):
    @property
    @abstractmethod
    def condition(self) -> INode: pass

    @property
    @abstractmethod
    def true_value(self) -> INode: pass

    @property
    @abstractmethod
    def false_value(self) -> INode: pass


class INodeWithArguments(INode):
    @property
    @abstractmethod
    def arguments(self) -> Iterable[INode]: pass


class INodeWithChildren(INode):
    @property
    @abstractmethod
    def children(self) -> Iterable[INode]: pass


class IStaticNode(INode):
    @property
    @abstractmethod
    def value(self) -> object: pass


class ArgumentCollection(Iterable[INode]):
    @property
    def has_items(self): return self.__items is not None and len(self.__items) > 0

    def __iter__(self):
        iter(self.__items)

    def __init__(self, items: Iterable[INode]):
        if items is None:
            self.__items = []  # type: List[INode]
        else:
            self.__items = list(items)

    def __str__(self):
        s = ''
        if self.has_items:
            s += StringTokens.ARGUMENTS_OPEN
            s += StringTokens.ARGUMENTS_SEPARATOR.join(self)
            s += StringTokens.ARGUMENTS_CLOSE
        return s


class CloseTag(IExpressionNode):
    @property
    def tag(self): return self.__tag

    @property
    def flags(self): return NodeFlags.IsExpression | NodeFlags.IsStatic

    def __init__(self, tag: TagType):
        self.__tag = tag

    def __str__(self):
        return "%s%s%s%s" % (StringTokens.TAG_OPEN,
                             StringTokens.ELEMENT_CLOSE,
                             self.tag,
                             StringTokens.TAG_CLOSE)

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)

    def evaluate(self, parameters: 'EvaluationParameters'):
        return expressions.CloseTag(self.tag)


class DefaultElement(INode):
    @property
    def tag(self): return self.__tag

    @property
    def data(self) -> INode: return self.__data

    @property
    def flags(self): return NodeFlags.IsStatic

    def __init__(self, tag: TagType, inner_buffer: bytes):
        self.__tag = tag
        self.__data = StaticByteArray(inner_buffer)

    def __str__(self):
        s = ''
        s += StringTokens.TAG_OPEN
        s += self.tag
        if len(self.__data.value) == 0:
            s += StringTokens.ELEMENT_CLOSE
            s += StringTokens.TAG_CLOSE
        else:
            s += StringTokens.TAG_CLOSE
            s += str(self.__data)
            s += StringTokens.TAG_OPEN
            s += StringTokens.ELEMENT_CLOSE
            s += str(self.tag)
            s += StringTokens.TAG_CLOSE
        return s

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)


class EmptyElement(INode):
    @property
    def tag(self): return self.__tag

    @property
    def flags(self): return NodeFlags.IsStatic

    def __init__(self, tag: TagType):
        self.__tag = tag

    def __str__(self):
        return "%s%s%s%s" % (StringTokens.TAG_OPEN,
                             self.tag,
                             StringTokens.ELEMENT_CLOSE,
                             StringTokens.TAG_CLOSE)

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)


class GenericElement(INodeWithChildren, INodeWithArguments, IExpressionNode):
    @property
    def tag(self): return self.__tag

    @property
    def arguments(self): return self.__arguments

    @property
    def content(self) -> INode: return self.__content

    @property
    def flags(self):
        f = NodeFlags.IsExpression
        if self.__arguments.has_items:
            f |= NodeFlags.HasArguments
        if self.content is not None:
            f |= NodeFlags.HasChildren
        return f

    def __init__(self, tag: TagType, content: INode, *args):
        self.__tag = tag
        self.__arguments = ArgumentCollection(*args)
        self.__content = content

    def __str__(self):
        s = ''
        s += StringTokens.TAG_OPEN
        s += self.tag
        s += str(self.__arguments)

        if self.content is None:
            s += StringTokens.ELEMENT_CLOSE
            s += StringTokens.TAG_CLOSE
        else:
            s += StringTokens.TAG_CLOSE
            s += str(self.content)
            s += StringTokens.TAG_OPEN
            s += StringTokens.ELEMENT_CLOSE
            s += str(self.tag)
            s += StringTokens.TAG_CLOSE
        return s

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)

    @property
    def children(self):
        return iter(self.content)

    def evaluate(self, parameters: 'EvaluationParameters'):
        return parameters.function_provider.evaluate_generic_element(parameters, self)


class OpenTag(IExpressionNode):
    @property
    def tag(self): return self.__tag

    @property
    def flags(self): return NodeFlags.IsExpression

    @property
    def arguments(self): return self.__arguments

    def __init__(self, tag: TagType, *args):
        self.__tag = tag
        self.__arguments = ArgumentCollection(*args)

    def __str__(self):
        s = StringTokens.TAG_OPEN
        s += str(self.tag)
        s += str(self.__arguments)
        s += StringTokens.TAG_CLOSE
        return s
        # return "%s%s%s%s" % (StringTokens.TAG_OPEN,
        #                      self.tag,
        #                      self.__arguments,
        #                      StringTokens.TAG_CLOSE)

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)

    def evaluate(self, parameters: 'EvaluationParameters'):
        return expressions.OpenTag(self.tag, [arg.evaluate(parameters) for arg in self.arguments])


class StaticByteArray(IStaticNode):
    @property
    def tag(self): return TagType.none

    @property
    def flags(self): return NodeFlags.IsStatic

    @property
    def value(self) -> bytes: return self.__value

    def __init__(self, value: bytes):
        self.__value = value

    def __str__(self):
        return self.value.hex().upper()

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)


class StaticInteger(IStaticNode):
    @property
    def tag(self): return TagType.none

    @property
    def flags(self): return NodeFlags.IsStatic

    @property
    def value(self) -> int: return self.__value

    def __init__(self, value: int):
        self.__value = value

    def __str__(self):
        return str(self.value)

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)


class StaticString(IStaticNode):
    @property
    def tag(self): return TagType.none

    @property
    def flags(self): return NodeFlags.IsStatic

    @property
    def value(self) -> str: return self.__value

    def __init__(self, value: str):
        self.__value = value

    def __str__(self):
        return str(self.value)

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)


class TopLevelParameter(IExpressionNode):
    @property
    def tag(self): return TagType.none

    @property
    def flags(self): return NodeFlags.IsExpression

    @property
    def value(self) -> int: return self.__value

    def __init__(self, value: int):
        self.__value = value

    def __str__(self):
        return "%s%s%s%s" % (StringTokens.TOP_LEVEL_PARAMETER_NAME,
                             StringTokens.ARGUMENTS_OPEN,
                             self.value,
                             StringTokens.ARGUMENTS_CLOSE)

    def accept(self, visitor: INodeVisitor[T]):
        return visitor.visit(self)

    def evaluate(self, parameters: 'EvaluationParameters'):
        return expressions.GenericExpression(parameters.top_level_parameters[self.value])
