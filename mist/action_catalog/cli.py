import sys
import argparse

from mist.sdk import config, MistException

from .catalog_add import *
from .catalog_list import catalog_list
from .catalog_index import index_catalog
from .catalog_delete import catalog_delete
from .catalog_search import catalog_search

def load_cli_catalog_values(d, parsed: argparse.Namespace):
    d.update(parsed.__dict__)


class CliCatalog(object):

    def __init__(self):
        self._default_action = False

        parser = argparse.ArgumentParser(
            description='MIST catalog manager',
            usage='''mist catalog <command> [<args>]

Available commands are:
   list        Displays installed catalogs (default option)
   add         Add new catalog
   delete      Delete existing catalog
   search      Search in catalog
   reindex     Re-index catalog database
   help        Displays help menu
_
''')
        parser.add_argument('command', help='Subcommand to run', nargs="*")

        if len(sys.argv) < 3:
            parser.print_usage()
            exit(0)

        actions = [*[x for x in dir(self) if not x.startswith("_")], "help"]

        if sys.argv[2] not in actions:
            self._default_action = True
            self.summary()
        else:
            parsed_args = parser.parse_args(sys.argv[2:3])
            if parsed_args.command[0] == "help":
                parser.print_usage()
                exit(0)
            else:
                # use dispatch pattern to invoke method with same name
                getattr(self, parsed_args.command[0])()

    def __parse__(self, parser) -> argparse.Namespace:

        if self._default_action:
            parsed_args = parser.parse_args(sys.argv[2:])
        else:
            parsed_args = parser.parse_args(sys.argv[3:])

        load_cli_catalog_values(config, parsed_args)

        return parsed_args


    def list(self):
        parser = argparse.ArgumentParser(
            description='Displays executions summary')
        parser.add_argument('MIST_DB')
        parser.add_argument('-i', '--row-id',
                            required=True,
                            help="register ID which get details")

        parsed_args = self.__parse__(parser)

        catalog_list(parsed_args)

    def add(self):

        parser = argparse.ArgumentParser(description='Add new catalog')
        parser.add_argument('CATALOG')

        parsed_args = self.__parse__(parser)

        try:
            catalog_add(parsed_args)
        except MistException as e:
            print("")
            print("[!]", str(e))
            print("")

    def delete(self):

        parser = argparse.ArgumentParser(
            description='Displays executions consoled for a execution')
        parser.add_argument('MIST_DB')
        parser.add_argument('-i', '--row-id',
                            required=True,
                            help="register ID which get details")

        parsed_args = self.__parse__(parser)

        catalog_delete(parsed_args)

    def search(self):

        parser = argparse.ArgumentParser(
            description='Checks console and database signatures')
        parser.add_argument('MIST_DB')
        parser.add_argument('-s', '--signature-file',
                            default=None,
                            help="signature file. usuallyy with .db.signature")
        parser.add_argument('-q', '--quiet',
                            action="store_true",
                            default=False,
                            help="hide log. Only summary message")

        parsed_args = self.__parse__(parser)

        #
        # Setup database
        #
        catalog_search(parsed_args)



    def reindex(self):
        index_catalog()


