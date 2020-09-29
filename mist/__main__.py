import os
import sys
import argparse
import platform
import pkg_resources

from http.server import HTTPServer

from mist.sdk import config, db

from .action_log import do_log
from .editor import EditorServer
from .interpreter import execute, check
from .exceptions import MistMissingBinaryException

HERE = os.path.dirname(__file__)


class Mist(object):

    def __init__(self):
        self._default_action = False

        parser = argparse.ArgumentParser(
            description='MIST - programing language for security made easy',
            usage='''mist <command> [<args>]

Available commands are:
   help       Displays help menu
   version    Displays installed MIST version
   exec       Run a .mist file (default option)
   check      Check a .mist file without execute them
   editor     Run live editor on browser
''')
        parser.add_argument('command', help='Subcommand to run', nargs="*")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        actions = [x for x in dir(self) if not x.startswith("_")]

        if sys.argv[1] not in actions:
            self._default_action = True
            self.exec()
        else:
            parsed_args = parser.parse_args(sys.argv[1:2])
            # use dispatch pattern to invoke method with same name
            getattr(self, parsed_args.command[0])()

    def version(self):
        print(f"version: {pkg_resources.get_distribution('mist').version}")
        print()
        exit()

    def exec(self):
        parser = argparse.ArgumentParser(
            description='execute a .mist file')
        parser.add_argument('MIST_FILE')
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

        db_group = parser.add_argument_group("Database")
        db_group.add_argument('-p', '--persist',
                            action="store_true",
                            help="persist database information to disk",
                            default=False)
        db_group.add_argument('-db', '--database-path',
                            help="database path file",
                            default=None)

        if self._default_action:
            parsed_args = parser.parse_args(sys.argv[1:])
        else:
            parsed_args = parser.parse_args(sys.argv[2:])

        #
        # Load console config
        #
        config.load_cli_values(parsed_args)

        #
        # Setup database
        #
        if config.persist:
            if config.database_path:
                if not config.database_path.endswith("db"):
                    config.database_path = f"{config.database_path}.db"

                db.setup(f"sqlite3://{config.database_path}")
            else:
                db.setup(f"sqlite3://{config.MIST_FILE}.db")

        try:
            execute(parsed_args)
        except MistMissingBinaryException as e:
            print("")
            print("[!] ", e)
            print()

    def log(self):

        parser = argparse.ArgumentParser(
            description='Manage logs for MIST executions')
        parser.add_argument('MIST_DB')

        parsed_args = parser.parse_args(sys.argv[2:])

        #
        # Load console config
        #
        config.load_cli_values(parsed_args)

        #
        # Setup database
        #
        db.setup(f"sqlite3://{config.MIST_DB}")

        #
        # Load console config
        #
        config.load_cli_values(parsed_args)

        #
        # Setup database
        #
        do_log(parsed_args)

    def check(self):
        parser = argparse.ArgumentParser(
            description='check a .mist file without execute')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('MIST_FILE')

        parsed_args = parser.parse_args(sys.argv[2:])

        try:
            check(parsed_args)

            print(f"[*] File '{parsed_args.MIST_FILE}' is ok")
        except Exception as e:

            print(f"[!] Parsing error:")
            print(str(e))

    def editor(self):

        print("[*] Starting editor at port 9000")
        print('''

        Open in your browser: http://localhot:9000
        
        BE CAREFUL: YOU MUST USE 'localhost' NOT '127.0.0.1'
        
        ''')
        httpd = HTTPServer(('localhost', 9000), EditorServer)
        httpd.serve_forever()

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

    Mist()


if __name__ == '__main__':
    main()
