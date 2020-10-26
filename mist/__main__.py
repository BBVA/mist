import os
import argparse
import platform

from pathlib import Path

from mist.action_run import cli_run
from mist.action_log import cli_log
from mist.action_editor import cli_editor
from mist.action_catalog import CORE_CATALOG, Catalog


HERE = os.path.dirname(__file__)

def build_cli() -> argparse.ArgumentParser:

    def _show_help(arg):
        print('''usage: mist <command> [<args>]

Available commands:
   run        Run a .mist file (default option)
   log        Manage execution log of MIST database
   help       Displays help menu
   editor     Run live editor on browser
   version    Displays installed MIST version
   catalog    Manage MIST catalogs

MIST Log manager

optional arguments:
  -h, --help            show this help message and exit
        ''')

    parser = argparse.ArgumentParser(
        prog='mist',
        description='MIST - programing language for security made easy',
        add_help=False)
    parser.add_argument('-h', '--help',
                      action="store_true",
                      help="show this help message and exit")
    parser.set_defaults(func=_show_help)
    subparsers = parser.add_subparsers()

    cli_run(subparsers)
    cli_log(subparsers)
    cli_editor(subparsers)

    return parser


def main():

    #
    # Check python version
    #
    if platform.python_version_tuple() < ("3", "8"):
        print("\n[!] Python 3.8 or above is required\n")
        print("If you don't want to install Python 3.8. "
              "Try with Docker:\n")
        print("   $ docker run --rm cr0hn/mist -h")
        exit(1)

    #
    # Checks if ~/.mist is created and download core catalog
    #
    home = Path().home().joinpath(".mist")

    if not home.exists():
        home.mkdir()

    if not home.joinpath("catalog").exists():
        home.joinpath("catalog").mkdir(parents=True)

    if not home.joinpath("catalog").joinpath("catalog.db").exists():
        catalog_path = Catalog.add_catalog(CORE_CATALOG)
        Catalog.index_catalog(catalog_path, CORE_CATALOG)

    main_parser = build_cli()

    parsed_args = main_parser.parse_args()
    if "func" in parsed_args:
        parsed_args.func(parsed_args)


if __name__ == '__main__':
    main()
