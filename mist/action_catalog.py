import os
import sys
import shutil
import json
import hashlib
import datetime
import argparse
from collections import namedtuple
from pathlib import Path
from textwrap import wrap

import pygit2

from terminaltables import SingleTable

from mist.helpers import download, file_uri_to_path
from mist.sdk import db, config, MistException
from mist.sdk.cmd import _DB_TABLE_NAME, _DB_TABLE_FIELDS


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


def catalog_path() -> Path:
    mist_home = Path().home().joinpath(".mist")

    if not mist_home.exists():
        mist_home.mkdir()

    return mist_home.joinpath("catalog")

def catalog_add(parsed: argparse.Namespace):
    catalog = parsed.CATALOG
    mist_catalog = catalog_path()

    git_providers = {
        "https://github.com",
        "https://gitlab.com",
        "https://bitbucket.org",
    }

    #
    # Import remote catalog
    #

    # Check if is a git repository
    if catalog.startswith("http"):
        if any(p in catalog for p in git_providers):
            if not catalog.endswith("git"):
                catalog = f"{catalog}.git"
            else:
                dst = str(file_uri_to_path(catalog)).replace(".git", "")[1:]

            dst = mist_catalog.joinpath(dst)

            if not dst.exists():
                dst.mkdir(parents=True)

            try:
                pygit2.clone_repository(catalog, str(dst))
            except ValueError:
                raise MistException("Catalog already exits")

        # Check if is a remote web
        else:
            dst = str(file_uri_to_path(catalog)).replace(".git", "")[1:]

            try:
                download(catalog, dst)
            except Exception as e:
                MistException(
                    f"Error while try to download catalog: '{catalog}'"
                )

    # Checks if is pa existing path
    elif os.path.exists(catalog):
        shutil.copy(catalog, mist_catalog)

    else:
        raise MistException(
            "Can't find catalog. If you are trying to add a remote catalog"
            "it must starts as 'http://' or 'https://'"
        )

    #
    # Parse and indexing catalog
    #

def catalog_delete(parsed: argparse.Namespace):
    pass

def catalog_search(parsed: argparse.Namespace):
    pass

def catalog_list(parsed: argparse.Namespace):
    pass


