import os
import argparse
import platform
import pkg_resources

from pathlib import Path

from mist.action_run import cli_run
from mist.action_server import cli_server

HERE = os.path.dirname(__file__)

def build_cli() -> argparse.ArgumentParser:

    def handler_version(parsed: argparse.Namespace):
        print()
        print(f"MIST version: "
              f"{pkg_resources.get_distribution('mist-lang').version}")
        print()
        exit()

    def _show_help(arg):
        print('''usage: mist <command> [<args>]

Available commands:
   run        Run a .mist file
   help       Displays help menu
   server     Run live editor on browser
   version    Displays installed MIST version

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

    #
    # Small top level actions
    #
    help_action = subparsers.add_parser("version",
                                        prog="mist vesion",)
    help_action.set_defaults(func=handler_version)

    help_action = subparsers.add_parser("help",
                                        prog="mist help",)
    help_action.set_defaults(func=handler_version)

    cli_run(subparsers)
    cli_server(subparsers)

    return parser


def main():

    #
    # Check python version
    #
    if platform.python_version_tuple() < ("3", "8"):
        print("\n[!] Python 3.8 or above is required\n")
        print("If you don't want to install Python 3.8. "
              "Try with Docker:\n")
        print("   $ docker run --rm bbvalabs/mist -h")
        exit(1)

    main_parser = build_cli()

    parsed_args = main_parser.parse_args()
    if "func" in parsed_args:
        parsed_args.func(parsed_args)

if __name__ == '__main__':
    main()
