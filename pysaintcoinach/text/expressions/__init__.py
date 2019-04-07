from abc import abstractmethod, ABC
from typing import Iterable, List

from text.utils import TagType, StringTokens


class IExpression(ABC):
    @abstractmethod
    def __str__(self): pass


class IValueExpression(IExpression):
    @property
    @abstractmethod
    def value(self) -> object: pass


class CloseTag(IExpression):
    @property
    def tag(self): return self.__tag

    def __init__(self, tag: TagType):
        self.__tag = tag

    def __str__(self):
        return "%s%s%s%s" % (StringTokens.TAG_OPEN,
                             StringTokens.ELEMENT_CLOSE,
                             self.tag,
                             StringTokens.TAG_CLOSE)


class ExpressionCollection(IExpression):
    @property
    def children(self) -> Iterable[IExpression]: return self.__children

    def __init__(self, *args):
        if len(args) == 0:
            self.__children = []  # type: List[IExpression]
        else:
            self.__children = list(*args)
        self.separator = ''

    def __str__(self):
        return self.separator.join(filter(None, self.children))


class GenericExpression(IValueExpression):
    @property
    @classmethod
    def empty(cls): return cls(None)

    @property
    def value(self): return self.__value

    def __init__(self, value: object):
        self.__value = value

    def __str__(self):
        if self.value is None:
            return ''
        return self.value


class OpenTag(IExpression):
    @property
    def tag(self): return self.__tag

    @property
    def arguments(self): return self.__arguments

    def __init__(self, tag: TagType, arguments: Iterable[IExpression]):
        self.__tag = tag
        if arguments is not None:
            self.__arguments = list(arguments)
        else:
            self.__arguments = []  # List[IExpression]

    def __str__(self):
        s = StringTokens.TAG_OPEN + self.tag
        if len(self.__arguments) > 0:
            s += StringTokens.ARGUMENTS_OPEN
            s += StringTokens.ARGUMENTS_SEPARATOR.join(self.__arguments)
            s += StringTokens.ARGUMENTS_CLOSE
        s += StringTokens.TAG_CLOSE
        return s


class SurroundedExpression(IValueExpression):
    @property
    def prefix(self) -> object: return self.__prefix

    @property
    def value(self) -> object: return self.__value

    @property
    def suffix(self) -> object: return self.__suffix

    def __init__(self, prefix: object, value: object, suffix: object):
        self.__prefix = prefix
        self.__value = value
        self.__suffix = suffix

    def __str__(self):
        return "%s%s%s" % (self.prefix,
                           self.value,
                           self.suffix)
