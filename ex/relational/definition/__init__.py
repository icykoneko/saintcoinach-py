from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Iterable, Union
from collections import OrderedDict
import io
from copy import copy
import operator
import itertools
import yaml
import json


class IDataDefinition(object):
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def convert(self, row: 'IDataRow', value: object, index: int) -> object:
        pass

    @abstractmethod
    def get_name(self, index: int) -> str:
        pass

    @abstractmethod
    def get_value_type_name(self, index: int) -> str:
        pass

    @abstractmethod
    def get_value_type(self, index: int) -> type:
        pass

    @abstractmethod
    def __copy__(self) -> 'IDataDefinition':
        pass

    @abstractmethod
    def to_json(self) -> OrderedDict:
        pass


class PositionedDataDefinition(yaml.YAMLObject):
    @property
    def inner_definition(self) -> IDataDefinition:
        return self.__inner_definition

    @inner_definition.setter
    def inner_definition(self, value):
        self.__inner_definition = value

    def __len__(self):
        return len(self.inner_definition or ())

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value

    def __init__(self, index=0, inner_definition=None):
        self.__index = index
        self.__inner_definition = inner_definition

    def __repr__(self):
        return "%s(Index=%r, InnerDefinition=%r)" % (
            self.__class__.__name__,
            self.index,
            self.inner_definition)

    def __getstate__(self):
        return {'Index': self.index,
                'InnerDefinition': self.inner_definition}

    def __setstate__(self, state):
        self.index = state.get('Index', 0)
        self.inner_definition = state.get('InnerDefinition', None)

    def __copy__(self):
        clone = PositionedDataDefinition(self.index, copy(self.inner_definition))
        return clone

    def convert(self, row, value, index):
        inner_index = index - self.index
        if inner_index < 0 or inner_index >= len(self):
            raise ValueError("'index' out of range")

        return self.inner_definition.convert(row, value, inner_index)

    def get_name(self, index):
        inner_index = index - self.index
        if inner_index < 0 or inner_index >= len(self):
            raise ValueError("'index' out of range")

        return self.inner_definition.get_name(inner_index)

    def get_value_type_name(self, index):
        inner_index = index - self.index
        if inner_index < 0 or inner_index >= len(self):
            raise ValueError("'index' out of range")

        return self.inner_definition.get_value_type_name(inner_index)

    def get_value_type(self, index):
        inner_index = index - self.index
        if inner_index < 0 or inner_index >= len(self):
            raise ValueError("'index' out of range")

        return self.inner_definition.get_value_type(inner_index)

    def to_json(self) -> OrderedDict:
        obj = self.inner_definition.to_json()
        if self.index > 0:
            obj['index'] = self.index
            obj.move_to_end('index', False)
        return obj

    @staticmethod
    def from_json(obj: dict):
        retv = PositionedDataDefinition()
        retv.index = int(obj.get('index', 0))
        retv.inner_definition = DataDefinitionSerializer.from_json(obj)
        return retv


class GroupDataDefinition(yaml.YAMLObject, IDataDefinition):
    yaml_tag = u'tag:yaml.org,2002:group_def'

    @property
    def members(self) -> List[IDataDefinition]:
        return self.__members

    @members.setter
    def members(self, value):
        self.__members = value

    def __len__(self):
        return sum(map(operator.length_hint, self.members))

    def __copy__(self):
        clone = GroupDataDefinition()
        for member in self.members:
            clone.members.append(copy(member))

        return clone

    def __init__(self):
        self.__members = []

    def __repr__(self):
        return "%s(Members=%r)" % (
            self.__class__.__name__,
            self.members)

    def __getstate__(self):
        return {'Members': self.members}

    def __setstate__(self, state):
        self.members = state.get('Members', [])

    def convert(self, row: 'IDataRow', value: object, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        converted_value = value
        pos = 0
        for member in self.members:
            new_pos = pos + len(member)
            if new_pos > index:
                inner_index = index - pos
                converted_value = member.convert(row, value, inner_index)
                break
            pos = new_pos
        return converted_value

    def get_name(self, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        value = None
        pos = 0
        for member in self.members:
            new_pos = pos + len(member)
            if new_pos > index:
                inner_index = index - pos
                value = member.get_name(inner_index)
                break
            pos = new_pos
        return value

    def get_value_type_name(self, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        value = None
        pos = 0
        for member in self.members:
            new_pos = pos + len(member)
            if new_pos > index:
                inner_index = index - pos
                value = member.get_value_type_name(inner_index)
                break
            pos = new_pos
        return value

    def get_value_type(self, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        value = None
        pos = 0
        for member in self.members:
            new_pos = pos + len(member)
            if new_pos > index:
                inner_index = index - pos
                value = member.get_value_type(inner_index)
                break
            pos = new_pos
        return value

    def to_json(self):
        obj = OrderedDict()
        obj['type'] = 'group'
        obj['members'] = [m.to_json() for m in self.members]
        return obj

    @staticmethod
    def from_json(obj: dict):
        retv = GroupDataDefinition()
        retv.members = [DataDefinitionSerializer.from_json(m) for m in obj.get('members', [])]
        return retv


class RepeatDataDefinition(yaml.YAMLObject, IDataDefinition):
    yaml_tag = u'tag:yaml.org,2002:repeat_def'

    @property
    def naming_offset(self):
        return self.__naming_offset

    @naming_offset.setter
    def naming_offset(self, value):
        self.__naming_offset = value

    @property
    def repeat_count(self):
        return self.__repeat_count

    @repeat_count.setter
    def repeat_count(self, value):
        self.__repeat_count = value

    @property
    def repeated_definition(self) -> IDataDefinition:
        return self.__repeated_definition

    @repeated_definition.setter
    def repeated_definition(self, value):
        self.__repeated_definition = value

    def __len__(self):
        return self.repeat_count * len(self.repeated_definition or ())

    def __init__(self, naming_offset=0, repeat_count=0, repeated_definition=None):
        self.__naming_offset = naming_offset
        self.__repeat_count = repeat_count
        self.__repeated_definition = repeated_definition

    def __repr__(self):
        return "%s(NamingOffset=%r, RepeatCount=%r, RepeatedDefinition=%r)" % (
            self.__class__.__name__,
            self.naming_offset,
            self.repeat_count,
            self.repeated_definition)

    def __getstate__(self):
        return {'NamingOffset': self.naming_offset,
                'RepeatCount': self.repeat_count,
                'RepeatedDefinition': self.repeated_definition}

    def __setstate__(self, state):
        self.naming_offset = state.get('NamingOffset', 0)
        self.repeat_count = state.get('RepeatCount', 0)
        self.repeated_definition = state.get('RepeatedDefinition', None)

    def __copy__(self):
        return RepeatDataDefinition(self.naming_offset,
                                    self.repeat_count,
                                    copy(self.repeated_definition))

    def convert(self, row: 'IDataRow', value: object, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        inner_index = index % len(self.repeated_definition)
        return self.repeated_definition.convert(row, value, inner_index)

    def get_name(self, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        repeat_nr = int(index / len(self.repeated_definition))
        inner_index = index % len(self.repeated_definition)
        base_name = self.repeated_definition.get_name(inner_index)
        return "%s[%u]" % (base_name, repeat_nr + self.naming_offset)

    def get_value_type_name(self, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        inner_index = index % len(self.repeated_definition)
        return self.repeated_definition.get_value_type_name(inner_index)

    def get_value_type(self, index: int):
        if index < 0 or index >= len(self):
            raise ValueError("'index' out of range")

        inner_index = index % len(self.repeated_definition)
        return self.repeated_definition.get_value_type(inner_index)

    def to_json(self):
        obj = OrderedDict()
        obj['type'] = 'repeat'
        obj['count'] = self.repeat_count
        obj['definition'] = self.repeated_definition.to_json()
        return obj

    @staticmethod
    def from_json(obj: dict):
        retv = RepeatDataDefinition()
        retv.repeat_count = int(obj.get('count', 0))
        retv.repeated_definition = DataDefinitionSerializer.from_json(obj.get('definition', {}))
        return retv


class SingleDataDefinition(yaml.YAMLObject, IDataDefinition):
    yaml_tag = u'tag:yaml.org,2002:single_def'

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def converter(self) -> 'IValueConverter':
        return self.__converter

    @converter.setter
    def converter(self, value):
        self.__converter = value

    def __len__(self):
        return 1

    def __init__(self, name=None, converter=None):
        self.__name = name
        self.__converter = converter

    def __repr__(self):
        return "%s(Name=%r, Converter=%r)" % (
            self.__class__.__name__,
            self.name,
            self.converter)

    def __getstate__(self):
        return {'Name': self.name,
                'Converter': self.converter}

    def __setstate__(self, state):
        self.name = state.get('Name', None)
        self.converter = state.get('Converter', None)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(dumper.DEFAULT_MAPPING_TAG,
                                        data.__getstate__(),
                                        flow_style=None)

    def to_json(self):
        obj = OrderedDict()
        obj['name'] = self.name
        if self.converter is not None:
            obj['converter'] = self.converter.to_json()
        return obj

    @staticmethod
    def from_json(obj: dict):
        from ex.relational.value_converters import ColorConverter, IconConverter, MultiReferenceConverter, \
            SheetLinkConverter, GenericReferenceConverter, TomestoneOrItemReferenceConverter, ComplexLinkConverter
        converter_obj = obj.get('converter', None)  # type: dict
        converter = None
        if converter_obj is not None:
            _type = converter_obj.get('type', None)
            if _type == 'color':
                converter = ColorConverter.from_json(converter_obj)
            elif _type == 'generic':
                converter = GenericReferenceConverter.from_json(converter_obj)
            elif _type == 'icon':
                converter = IconConverter.from_json(converter_obj)
            elif _type == 'multiref':
                converter = MultiReferenceConverter.from_json(converter_obj)
            elif _type == 'link':
                converter = SheetLinkConverter.from_json(converter_obj)
            elif _type == 'tomestone':
                converter = TomestoneOrItemReferenceConverter.from_json(converter_obj)
            elif _type == 'complexlink':
                converter = ComplexLinkConverter.from_json(converter_obj)
            else:
                raise ValueError("Invalid converter type.")

        return SingleDataDefinition(
            name=obj.get('name', None),
            converter=converter)

    def __copy__(self):
        return SingleDataDefinition(self.name, self.convert)

    def convert(self, row: 'IDataRow', value: object, index: int):
        if index != 0:
            raise ValueError("'index' out of range")

        return value if self.converter is None else self.converter.convert(row, value)

    def get_name(self, index: int):
        if index != 0:
            raise ValueError("'index' out of range")

        return self.name

    def get_value_type_name(self, index: int):
        if index != 0:
            raise ValueError("'index' out of range")

        return None if self.converter is None else self.converter.target_type_name

    def get_value_type(self, index: int):
        if index != 0:
            raise ValueError("'index' out of range")

        return None if self.converter is None else self.converter.target_type


class DataDefinitionSerializer(object):
    @staticmethod
    def from_json(obj: dict) -> IDataDefinition:
        _type = obj.get('type', None)
        if _type is None:
            return SingleDataDefinition.from_json(obj)
        elif _type == 'group':
            return GroupDataDefinition.from_json(obj)
        elif _type == 'repeat':
            return RepeatDataDefinition.from_json(obj)
        else:
            raise ValueError("Invalid definition type.")


class SheetDefinition(yaml.YAMLObject):
    yaml_tag = u'SheetDefinition'

    @property
    def data_definitions(self) -> List[PositionedDataDefinition]:
        return self.__data_definitions

    @data_definitions.setter
    def data_definitions(self, value):
        self.__data_definitions = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def default_column(self):
        return self.__default_column

    @default_column.setter
    def default_column(self, value):
        self.__default_column = value

    @property
    def is_generic_reference_target(self):
        return self.__is_generic_reference_target

    @is_generic_reference_target.setter
    def is_generic_reference_target(self, value):
        self.__is_generic_reference_target = value

    def __init__(self,
                 data_definitions=None,
                 name=None,
                 default_column=None,
                 is_generic_reference_target=False):
        self.__column_definition_map = {}  # type: Dict[int, PositionedDataDefinition]
        self.__column_name_to_index_map = {}  # type: Dict[str, int]
        self.__column_index_to_name_map = {}  # type: Dict[int, str]
        self.__column_value_type_names = {}  # type: Dict[int, str]
        self.__column_value_types = {}  # type: Dict[int, type]
        self.__default_column_index = None
        self.__is_compiled = False

        self.__name = name
        self.__default_column = default_column
        self.__is_generic_reference_target = is_generic_reference_target
        self.__data_definitions = data_definitions or []

    def __repr__(self):
        return "%s(DataDefinitions=%r, Name=%r, DefaultColumn=%r, IsGenericReferenceTarget=%r)" % (
            self.__class__.__name__,
            self.data_definitions,
            self.name,
            self.default_column,
            self.is_generic_reference_target)

    def __getstate__(self):
        return {'DataDefinitions': self.data_definitions,
                'Name': self.name,
                'DefaultColumn': self.default_column,
                'IsGenericReferenceTarget': self.is_generic_reference_target}

    def __setstate__(self, state):
        self.__column_definition_map = {}  # type: Dict[int, PositionedDataDefinition]
        self.__column_name_to_index_map = {}  # type: Dict[str, int]
        self.__column_index_to_name_map = {}  # type: Dict[int, str]
        self.__column_value_type_names = {}  # type: Dict[int, str]
        self.__column_value_types = {}  # type: Dict[int, type]
        self.__default_column_index = None
        self.__is_compiled = False

        data_definitions = state.get('DataDefinitions', [])
        self.data_definitions = []
        for data_definition in data_definitions:
            o = PositionedDataDefinition()
            o.__setstate__(data_definition)
            self.data_definitions += [o]

        self.name = state.get('Name', None)
        self.default_column = state.get('DefaultColumn', None)
        self.is_generic_reference_target = state.get('IsGenericReferenceTarget', False)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(dumper.DEFAULT_MAPPING_TAG,
                                        data.__getstate__(),
                                        flow_style=None)

    def to_json(self) -> OrderedDict:
        obj = OrderedDict()
        obj['sheet'] = self.name
        if self.default_column is not None:
            obj['defaultColumn'] = self.default_column
        if self.is_generic_reference_target:
            obj['isGenericReferenceTarget'] = True
        obj['definitions'] = [dd.to_json() for dd in self.data_definitions]
        return obj

    @staticmethod
    def from_json(obj: dict):
        return SheetDefinition(
            name=obj.get('sheet', None),
            default_column=obj.get('defaultColumn', None),
            is_generic_reference_target=obj.get('isGenericReferenceTarget', False),
            data_definitions=[PositionedDataDefinition.from_json(j) for j in obj.get('definitions', [])])

    def compile(self):
        self.__column_definition_map = {}
        self.__column_name_to_index_map = {}
        self.__column_index_to_name_map = {}
        self.__column_value_type_names = {}
        self.__column_value_types = {}
        self.data_definitions.sort(key=operator.attrgetter('index'))
        for _def in self.data_definitions:
            for i in range(_def.index):
                offset = _def.index + i
                self.__column_definition_map[offset] = _def

                name = _def.get_name(offset)
                self.__column_name_to_index_map[name] = offset
                self.__column_index_to_name_map[offset] = name
                self.__column_value_type_names[offset] = _def.get_value_type_name(offset)
                self.__column_value_types[offset] = _def.get_value_type(offset)

        self.__default_column_index = self.__column_name_to_index_map.get(self.default_column)
        self.__is_compiled = True

    def get_definition(self, index) -> PositionedDataDefinition:
        if self.__is_compiled:
            return self.__column_definition_map[index]

        res = filter(lambda d: d.index <= index < (d.index + len(d)), self.data_definitions)
        return next(res, None)

    def get_default_column_index(self):
        if self.__is_compiled:
            return self.__default_column_index
        return None if len((self.default_column or '').strip()) == 0 else self.find_column(self.default_column)

    def find_column(self, column_name):
        if self.__is_compiled:
            return self.__column_name_to_index_map[column_name]

        for _def in self.data_definitions:
            for i in range(len(_def)):
                n = _def.get_name(_def.index + i)
                if str(n) == column_name:
                    return _def.index + i
        return None

    def get_all_column_names(self) -> Iterable[str]:
        if self.__is_compiled:
            return self.__column_name_to_index_map.keys()

        for _def in self.data_definitions:
            for i in range(len(_def)):
                yield _def.get_name(_def.index + i)

    def get_column_name(self, index):
        if self.__is_compiled:
            return self.__column_index_to_name_map.get(index)

        _def = self.get_definition(index)
        return _def.get_name(index) if _def is not None else None

    def get_value_type_name(self, index):
        if self.__is_compiled:
            return self.__column_value_type_names.get(index)

        _def = self.get_definition(index)
        return _def.get_value_type_name(index) if _def is not None else None

    def get_value_type(self, index):
        if self.__is_compiled:
            return self.__column_value_types.get(index)

        _def = self.get_definition(index)
        return _def.get_value_type(index) if _def is not None else None

    def convert(self, row, value, index):
        _def = self.get_definition(index)
        return _def.convert(row, value, index) if _def is not None else value


class RelationDefinition(yaml.YAMLObject):
    yaml_tag = u'RelationDefinition'

    @property
    def sheet_definitions(self) -> List[SheetDefinition]:
        return self.__sheet_definitions

    @sheet_definitions.setter
    def sheet_definitions(self, value):
        self.__sheet_definitions = value

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, value):
        self.__version = value

    def __init__(self):
        self.__is_compiled = False
        self.__sheet_definitions = []  # type: List[SheetDefinition]
        self.__sheet_map = {}  # type: Dict[str, SheetDefinition]
        self.__version = None

    def __repr__(self):
        return "%s(SheetDefinitions=%r, Version=%r)" % (
            self.__class__.__name__,
            self.sheet_definitions,
            self.version)

    def compile(self):
        self.__sheet_map = dict([(d.name, d) for d in self.__sheet_definitions])
        for sheet in self.sheet_definitions:
            sheet.compile()

        self.__is_compiled = True

    def get_sheet(self, name) -> SheetDefinition:
        if self.__is_compiled:
            return self.__sheet_map.get(name)

        res = filter(lambda d: d.name == name, self.sheet_definitions)
        return next(res, None)

    def get_or_create_sheet(self, name) -> SheetDefinition:
        _def = self.get_sheet(name)
        if _def is None:
            _def = SheetDefinition(name)
            self.sheet_definitions += [_def]
        return _def

    def to_json(self) -> OrderedDict:
        obj = OrderedDict()
        obj['version'] = self.version
        obj['sheets'] = [s.to_json() for s in sorted(self.sheet_definitions, key=lambda s: s.name)]
        return obj

    @staticmethod
    def from_json(obj: dict):
        retv = RelationDefinition()
        retv.version = obj.get('version', None)
        retv.sheet_definitions = [SheetDefinition.from_json(j) for j in obj.get('sheets', [])]
        return retv

    @staticmethod
    def from_json_fp(fp):
        #return json.loads(s, object_pairs_hook=SheetDefinition.from_json)
        obj = json.load(fp)
        return RelationDefinition.from_json(obj)

    def serialize(self, stream_or_path: Union[io.TextIOBase, str]):
        def with_stream(stream):
            yaml.dump(self, stream)

        if isinstance(stream_or_path, str):
            with open(stream_or_path, "w", encoding="utf-8") as stream:
                with_stream(stream)
        else:
            with_stream(stream_or_path)

    def deserialize(self, stream_or_path: Union[io.TextIOBase, str]):
        def with_stream(stream):
            yaml.load(stream)

        if isinstance(stream_or_path, str):
            with open(stream_or_path, "r", encoding="utf-8") as stream:
                with_stream(stream)
        else:
            with_stream(stream_or_path)

    def __setstate__(self, state):
        sheet_definitions = state.get('SheetDefinitions', [])
        # Need to convert each record into objects...
        self.sheet_definitions = []
        for sheet_definition in sheet_definitions:
            o = SheetDefinition()
            o.__setstate__(sheet_definition)
            self.sheet_definitions += [o]
        self.version = state.get('Version', None)
        self.__is_compiled = False

    def __getstate__(self):
        # Save only the serializable properties
        return {'SheetDefinitions': self.sheet_definitions,
                'Version': self.version}

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(dumper.DEFAULT_MAPPING_TAG,
                                        data.__getstate__(),
                                        flow_style=None)


class ViewColumnDefinition(object):
    @property
    def column_name(self) -> str: return self._column_name

    @property
    def converter(self) -> 'IValueConverter': return self._converter

    def __init__(self, **kwargs):
        self._column_name = kwargs.get('column_name', None)
        self._converter = kwargs.get('converter', None)

    @staticmethod
    def from_json(obj: dict):
        converter_obj = obj.get('converter')
        converter = None
        if converter_obj is not None:
            type = converter_obj['type']
            if type == 'quad':
                converter = QuadConverter.from_json(converter_obj)
            else:
                raise ValueError("Invalid converter type")
        return ViewColumnDefinition(column_name=obj['name'],
                                    converter=converter)


class ViewDefinition(object):
    @property
    def sheet_name(self) -> str: return self._sheet_name

    @property
    def column_definitions(self) -> List[ViewColumnDefinition]:
        return self._column_definitions

    def __init__(self, **kwargs):
        self._sheet_name = kwargs.get('sheet_name', None)
        self._column_definitions = kwargs.get('column_definitions', None)

    @staticmethod
    def from_json(obj: dict):
        return ViewDefinition(sheet_name=str(obj['sheet']),
                              column_definitions=ViewColumnDefinition.from_json(obj['columns']))
