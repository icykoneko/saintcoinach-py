from pathlib import Path
import json
import os
import logging
import yaml

try:
    _SCRIPT_PATH = os.path.abspath(__path__)
except:
    _SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

_EXDSCHEMA_HOME = Path(_SCRIPT_PATH, '..', 'EXDSchema')

from .ex import Language
from .ex.relational.definition import RelationDefinition, SheetDefinition
from .ex.relational.definition.exdschema import schema_util
from .ex.relational.definition.exdschema import Sheet as SchemaSheet
from .xiv import XivCollection
from .pack import PackCollection
from .indexfile import Directory
from .file import File

__all__ = ['ARealmReversed']


class ARealmReversed(object):
    """
    Central class for accessing game assets.
    """

    """File name containing the current version string."""
    _VERSION_FILE = 'ffxivgame.ver'

    @property
    def game_directory(self): return self._game_directory

    @property
    def packs(self): return self._packs

    @property
    def game_data(self): return self._game_data

    @property
    def game_version(self): return self._game_version

    @property
    def definition_version(self): return self.game_data.definition.version

    @property
    def is_current_version(self): return self.game_version == self.definition_version

    def __init__(self, game_path: str, language: Language):
        self._game_directory = Path(game_path)
        self._packs = PackCollection(self._game_directory.joinpath('game', 'sqpack'))
        self._game_data = XivCollection(self._packs)
        self._game_data.active_language = language

        self._game_version = self._game_directory.joinpath('game', 'ffxivgame.ver').read_text()
        self._game_data.definition = self.__read_definition()

        self._game_data.definition.compile()

    def __read_definition(self) -> RelationDefinition:
        _def = RelationDefinition(version='latest')
        for sheet_file_name in _EXDSCHEMA_HOME.glob('*.yml'):
            _yaml = sheet_file_name.read_text()
            try:
                sheet = SchemaSheet.from_yaml(_yaml)
                sheet = schema_util.flatten(sheet)
                sheet_def = SheetDefinition.from_yaml(sheet)
                _def.sheet_definitions.append(sheet_def)

                if not self._game_data.sheet_exists(sheet_def.name):
                    logging.warning('Defined sheet %s is missing', sheet_def.name)
            except yaml.error.YAMLError as exc:
                logging.exception('Failed to decode %s: %s', sheet_file_name, str(exc))

        return _def


# This is an example of how to use this library.
# XIV = ARealmReversed(r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
#                      Language.english)

def get_default_xiv():
    from . import text
    _string_decoder = text.XivStringDecoder.default()

    # Override the tag decoder for emphasis so it doesn't produce tags in string...
    def omit_tag_decoder(i, t, l):
        text.XivStringDecoder.get_integer(i)
        return text.nodes.StaticString('')

    _string_decoder.set_decoder(text.TagType.Emphasis.value, omit_tag_decoder)
    _string_decoder.set_decoder(
        text.TagType.SoftHyphen.value,
        lambda i,t,l: text.nodes.StaticString(_string_decoder.dash))

    return ARealmReversed(r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
                          Language.english)
