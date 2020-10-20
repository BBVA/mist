import os
import sys
import argparse
import platform
import pkg_resources

from pathlib import Path

from http.server import HTTPServer

from mist.catalog import CORE_CATALOG, Catalog
from mist.sdk import config, db, params, MistMissingBinaryException, \
    MistAbortException, MistInputDataException

from mist.action_log import CliLog
from mist.editor import EditorServer
from mist.action_exec import load_cli_exec_values, execute

HERE = os.path.dirname(__file__)


class Mist(object):

    def __init__(self):
        self._default_action = False

        parser = argparse.ArgumentParser(prog = 'mist',
            description='MIST - programing language for security made easy',
            usage='''mist <command> [<args>]

Programing language for security made easy

Available commands are:
   help       Displays help menu
   version    Displays installed MIST version
   exec       Run a .mist file (default option)
   log        Manage execution log of MIST database
   catalog    Manage MIST catalogs
   editor     Run live editor on browser


Execution examples:

    > mist exec my-program.mist
    > mist my-program.mist  # Same action that above command

Launching editor:

    > mist editor

Managing log:

    > mist log my-program.db

_
''',
            add_help = False)
        parser.add_argument('command', help='Subcommand to run', nargs="*")

        if len(sys.argv) < 2:
            parser.print_usage()
            exit(0)

        actions = [*[x for x in dir(self) if not x.startswith("_")], "help"]

        if sys.argv[1] not in actions:
            self._default_action = True
            self.exec()
        else:
            parsed_args = parser.parse_args(sys.argv[1:2])
            if parsed_args.command[0] == "help":
                parser.print_usage()
                exit(0)
            else:
                # use dispatch pattern to invoke method with same name
                getattr(self, parsed_args.command[0])()

    def version(self):
        print()
        print(f"MIST version: "
              f"{pkg_resources.get_distribution('mist-lang').version}")
        print()
        exit()

    def exec(self):
        parser = argparse.ArgumentParser(prog = 'mist exec',
            description='execute a .mist file',
            usage = '''%(prog)s [-h] [-N] [-C] [-R] [-d] [-S] [-p] [-db DATABASE_PATH] MIST_FILE [PARAMS ...]

execute a .mist file

positional arguments:
  MIST_FILE             MIST - FILE to execute
  PARAMS                Params for MIST - FILE param1=value1 ...

optional arguments:
  -h, --help            show help message and exit
  -N, --no-check-tools  do not check if tools are installed
  -C, --console-output  displays console output of executed tools
  -R, --real-time       display console output in real time
  -d, --debug           enable debug messages
  -S, --simulate        simulate without execute
  -db [DATABASE_PATH], --database-path [DATABASE_PATH]
                        database path file
''',
            add_help = False)
        parser.add_argument('OPTIONS',
                            help="MIST - FILE[param1 = value1 param2 = value2...]",
                            metavar="OPTIONS", nargs="+")
        parser.add_argument('-N', '--no-check-tools',
                            action="store_true",
                            help="do not check if tools are installed",
                            default=False)
        parser.add_argument('-C', '--console-output',
                            action="store_false",
                            help="displays console output of executed tools",
                            default=True)
        parser.add_argument('-R', '--real-time',
                            action="store_false",
                            help="display console output in real time",
                            default=True)
        parser.add_argument('-d', '--debug',
                            action="store_true",
                            help="enable debug messages",
                            default=False)
        parser.add_argument('-S', '--simulate',
                            action="store_true",
                            help="simulate without execute",
                            default=False)
        parser.add_argument('-db', '--database-path',
                            help="database path file",
                            nargs = '?',
                            const = 'default',
                            default=None)

        if self._default_action:
            parsed_args = parser.parse_args(sys.argv[1:])
        else:
            parsed_args = parser.parse_args(sys.argv[2:])

        #
        # Check if filename is passed as parameter
        #
        if not parsed_args.OPTIONS:
            print("[!] .mist file needed as first parameter")
            exit(1)

        #
        # Load console config
        #
        config.load_cli_values(parsed_args)
        load_cli_exec_values(params, parsed_args)

        #
        # Setup database
        #
        if config.database_path:
            if config.database_path != 'default':
                if not config.database_path.endswith("db"):
                    config.database_path = f"{config.database_path}.db"
                db.setup(f"sqlite3://{config.database_path}")
            else:
                db.setup(f"sqlite3://{config.MIST_FILE}.db")

        try:
            execute()
        except MistMissingBinaryException as e:
            print()
            print("[!] ", e)
            print()
        except MistInputDataException as e:
            print()
            print(str(e))
            print()

        except MistAbortException as e:
            ex_len = len(str(e))
            ex_step1 = int(ex_len / 2) - 4

            if ex_len % 2 != 0:
                ex_step2 = ex_step1 + 2
            else:
                ex_step2 = ex_step1 + 1

            print("!" * ( ex_len+ 4))
            print("!", " " * ex_step1 , "ABORT", " " * ex_step2 ,"!")
            print("!",  " " * ex_len, "!")
            print("!", e, "!")
            print("!",  " " * ex_len, "!")
            print("!" * (ex_len + 4))

            exit(1)
        except KeyboardInterrupt:
            print()
            print("[*] Closing session")
            print()
        finally:
            # Write database signature
            if db.db_path:
                signature_path = f"{db.db_path}.signature.txt"

                with open(signature_path, "w") as f:
                    f.write(db.signature())

    def log(self):
        CliLog()

    # def catalog(self):
    #     CliCatalog()

    def editor(self):

        print("[*] Starting editor at port 9000")
        print('''

        Open in your browser: http://localhot:9000

        BE CAREFUL: YOU MUST USE 'localhost' NOT '127.0.0.1'

        ''')
        httpd = HTTPServer(('localhost', 9000), EditorServer)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

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

    Mist()


if __name__ == '__main__':
    main()
