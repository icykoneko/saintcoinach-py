# pysaintcoinach

A Python port of the popular [Saint Coinach](https://github.com/ufx/SaintCoinach) library for extracting game assets and reading game assets from **Final Fantasy XIV**.

This library aims to provide a complete Python implementation of the C# library, attempting to showcase all the potential of the Python programming language, and to enable quick development of scripts for other projects.

Special thanks to @[ufx](https://github.com/ufx) and all contributors to the Saint Coinach library.

## Functionality

### Fully implemented and maintained

* Extraction of files from the game's SqPack files based on their friendly name (or by identifiers, if preferred).
* Conversion of the game's textures to `PIL`-based objects, using `Pillow`.
* Parsing and reading from the game's data files (`*.exh` and `*.exd`).
* Decoding of OGG files stored in the game's pack files.

### Partially implemented

* OO-representation of select game data.
* Decoding of the string format used by the game.

### Not implemented or ported

* Self-updating feature. This port relies on the original Saint Coinach library for `ex.json` mappings.

## Cloning this Repo

This repo makes use of submodules and symlinks. When cloning, please include the `--recurse-submodules` option.

If using Windows, you have a couple options for handling symlinks:

1. Follow the instructions in https://stackoverflow.com/questions/5917249/git-symlinks-in-windows, creating the command aliases. Then, after cloning, you should be able to just run `git submodule foreach --recursive git rm-symlinks` to convert them into hardlinks.
    * **NOTE:** You will need to run `git submodule foreach --recursive git checkout-symlinks` to restore the git symlinks.
2. Enable the permissions for creating symlinks in Git for Windows; see https://github.com/git-for-windows/git/wiki/Symbolic-Links.
    * **NOTE:** You need to start Git Bash in admin mode for it to create symlinks. If you forgot to do that during cloning, you'll need to follow the instructions in part 1 instead.

Alternatively, this workflow also works, and doesn't require any aliases. You do need to enable permissions, and will need to use admin mode for some parts:
```
git clone --recurse-submodules git@github.com:icykoneko/saintcoinach-py.git
git submodule foreach --recursive git config core.symlinks true
# As admin:
git submodule update --force --recursive
```

## Usage

Those familiar with Saint Coinach will find the API to be mostly unchanged; however, since this is a Python implementation, most, if not all the API is written in Pythonic form. Only class names have remained unchanged. Methods and properties are written in PEP-8 complient format, i.e. `SaintCoinach.Ex.Language.English` becomes `pysaintcoinach.ex.Language.english`, and properties such as `ARealmReversed.GameData` become `ARealmReversed.game_data`. Where possible, Pythonic representations of collections are used. As such, this library is only compatible with Python 3.X.

### Set-up

It's recommended you run `pysaintcoinach` with a virtual environment. A `requirements.txt` is provided to install the necessary 3rd-party modules.

```cmd
python3 -m venv pyvirt
.\pyvirt\Scripts\activate
pip install -r requirements.txt
```

All important data is exposed by the `pysaintcoinach.ARealmReversed` class, so setting up access to it is fairly straightforward.

The following is an example using the game's default installation path and English as the default language:

```python
import pysaintcoinach

GAME_DIRECTORY = r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn"
realm = pysaintcoinach.ARealmReversed(GAME_DIRECTORY, pysaintcoinach.ex.Language.english)
```

Alternatively, a special helper function is available for default installations which includes fixups for certain string tags:

```python
import pysaintcoinach

realm = pysaintcoinach.get_default_xiv()
```

### Accessing data

Game files can be accessed directly through `ARealmReversed.packs`. Game data can be accessed through `ARealmReversed.game_data`.

#### Game Data (`XivCollection`)

Each game data table (or sheet) is accessed using the `get_sheet(name)` method. For some collections, an OO-representation is available. Regardless of that, you can access mapped fields in a number of ways.

The following is a simple example that outputs the name and description of all `Weather` objects to the console:

```python
weathers = realm.game_data.get_sheet('Weather')
for weather in weathers:
    print("#{:>3}: {} -> {}".format(weather.key, weather.name, weather.description))
```

Next, we see how sheets are related. The following example outputs the available pet actions for each pet. This should give you an idea of just how useful this library can be.

```python
from itertools import groupby
from operator import methodcaller, itemgetter

# Filter out any actions which do not have a name, then sort by Pet id for grouping.
sorted_pet_actions = sorted(filter(lambda row: row.as_string('Name') != "",
                                   realm.game_data.get_sheet('PetAction')),
                            key=methodcaller('get_raw', 'Pet'))

for pet, pet_actions in groupby(sorted_pet_actions, key=itemgetter('Pet')):
    pet_name = pet['Name']
    if pet_name == "":
        pet_name = "all pets"
    print("Actions for {}:".format(pet_name))
    for pet_action in pet_actions:
        if pet_action.get_raw('Action') == 0:
            print("       {}: {}".format(pet_action['Name'],
                                         pet_action['Description']))
        else:
            print("  Lv{:<2} {}: {}".format(pet_action['Action']['ClassJobLevel'],
                                            pet_action['Name'],
                                            pet_action['Description']))
    print("")
```

As a bonus, the `pysaintcoinach.exdhelper.ExdHelper` class can dump an entire sheet or row to a dictionary for interactive inspection. Keep in mind, although it may look like certain field values are mere strings, if they came from a linked sheet, the actual value is the entire row. That said, you should not use `ExdHelper` as your primary method of reading data as it is far less efficient.

## Notes

### Documentation

Aside from this readme, there's not much in the way of function documentation. As with the original Saint Coinach library, there should be enough documentation available to know how to use the library for game data, but figuring out the internal working... yea, it's a challenge.

## Contributing to the code base

As this library is a port, any feature-related contributions should be directed towards [Saint Coinach](https://github.com/ufx/SaintCoinach). Bug-fixes with this port may be contributed.

## Licenses and Attribution

The majority of this library's functionality was ported from [Saint Coinach](https://github.com/ufx/SaintCoinach) and is licensed under the WTFPL. This port is licensed under the terms of the MIT license. For more information, please refer to [LICENSE](LICENSE).

FINAL FANTASY XIV © 2010 - 2019 SQUARE ENIX CO., LTD. All Rights Reserved.

FINAL FANTASY, FINAL FANTASY XIV, FFXIV, and SQUARE ENIX are registered trademarks of Square Enix Holdings Co., Ltd.