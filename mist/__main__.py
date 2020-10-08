import os
import sys
import argparse
import platform
import pkg_resources

from http.server import HTTPServer

from mist.sdk import config, db, params, MistMissingBinaryException, \
    MistAbortException, MistInputDataException

from mist.action_log import CliLog
from mist.editor import EditorServer
from mist.interpreter import execute

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
   log        Manage execution log of MIST database
   editor     Run live editor on browser


Execution examples:

    > mist exec my-program.mist
    > mist my-program.mist  # Same action that above command

Launching editor: 
    
    > mist editor

Managing log: 

    > mist log my-program.db
    
_
''')
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
        parser = argparse.ArgumentParser(
            description='execute a .mist file')
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
        # Check if filename is passed as parameter
        #
        if not parsed_args.OPTIONS:
            print("[!] .mist file needed as first parameter")
            exit(1)

        #
        # Load console config
        #
        config.load_cli_values(parsed_args)
        params.load_cli_values(parsed_args)

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

    Mist()


if __name__ == '__main__':
    main()
