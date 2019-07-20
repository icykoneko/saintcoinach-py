import logging

from pysaintcoinach import ARealmReversed
from pysaintcoinach.ex import Language
from pysaintcoinach.cmd.xivshell import XivShell


logging.basicConfig()
logger = logging.getLogger('xivshell')
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(type=str,
                        default=r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
                        dest='data_path',
                        nargs='?',
                        help='Path to FF14 installation')

    args = parser.parse_args()

    realm = ARealmReversed(args.data_path, Language.english)

    logger.info('Game version:       {0}'.format(realm.game_version))
    logger.info('Definition version: {0}'.format(realm.definition_version))

    if not realm.is_current_version:
        logger.warning('Definitions appear to be out-of-date!')

    XivShell(realm).cmdloop()
