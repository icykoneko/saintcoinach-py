from pathlib import Path
import json

from ex import Language, ViewCollection
from ex.relational.definition import RelationDefinition
from xiv import XivCollection
from pack import PackCollection

from indexfile import Directory
from file import File


class ARealmReversed(object):
    _DEFINITION_FILE = 'ex.json'
    _VIEW_DEFINITION_FILE = 'exview.json'
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

    @property
    def views(self): return self._views

    def __init__(self, game_path: str, language: Language):
        self._game_directory = Path(game_path)
        self._packs = PackCollection(self._game_directory.joinpath('game', 'sqpack'))
        self._game_data = XivCollection(self._packs)
        self._game_data.active_language = language
        self._game_version = self._game_directory.joinpath('game', 'ffxivgame.ver').read_text()
        self._views = self._read_view_collection()

        with open(self._DEFINITION_FILE, 'r', encoding='utf-8') as f:
            self._game_data.definition = RelationDefinition.from_json_fp(f)

    def _read_view_collection(self):
        view_file = Path(self._VIEW_DEFINITION_FILE)
        with view_file.open(encoding='utf-8') as f:
            return ViewCollection.from_json(json.load(f))


XIV = ARealmReversed(r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
                     Language.english)
