import sys
import argparse
import platform

import pkg_resources

from mist.sdk import config, db

from .interpreter import execute, check


class Mist(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='MIST - programing language for security made easy',
            usage='''mist <command> [<args>]

Available commands are:
   version    Displays installed MIST version
   exec       Run a .mist file (default option)
   check      Check a .mist file without execute them
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        parsed_args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, parsed_args.command):
            self.exec()
        else:
            # use dispatch pattern to invoke method with same name
            getattr(self, parsed_args.command)()

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
        parser.add_argument('-p', '--persist',
                            action="store_true",
                            help="persist database information to disk",
                            default=False)

        if sys.argv[1] == "exec":
            in_args = sys.argv[2:]
        else:
            in_args = sys.argv[1:]

        parsed_args = parser.parse_args(in_args)

        #
        # Load console config
        #
        config.load_cli_values(parsed_args)

        #
        # Setup database
        #
        if config.persist:
            db.setup(f"sqlite3://{config.MIST_FILE}.db")

        execute(parsed_args)



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
