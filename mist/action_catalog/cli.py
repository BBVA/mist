import json
import argparse

from terminaltables import SingleTable

from .catalog import Catalog

def show_help(args):
    print('''usage: mist catalog <command> [<args>]

Available commands:
   list      List available catalog
   add       Add new catalog
   delete    Delete exiting catalog
   search    Search command in installed catalogs
   reindex   Update catalog database

MIST catalog manager

optional arguments:
  -h, --help            show this help message and exit
''')

def handler_list(parsed: argparse.Namespace):

    table_content = [
        ["ID", "URL", "Local Path"]
    ]

    for cat in Catalog.find_catalog():
        table_content.append(
            [
                cat["id"],
                cat["uri"],
                cat["local_path"]
            ]
        )

    table = SingleTable(table_content,
                        title="Available catalogs ")
    table.inner_row_border = True

    print("")
    print(table.table)
    print("")

def handler_add(parsed: argparse.Namespace):
    catalog_uri = parsed.CATALOG_URI

    catalog_path = Catalog.add_catalog(catalog_uri)

def handler_reindex(parsed: argparse.Namespace):

    print("[*] Re-indexing catalog...", end='', flush=True)
    Catalog.reindex()
    print("done", flush=True)

def handler_delete(parsed: argparse.Namespace):
    catalog_id = parsed.CATALOG_ID

    print()

    if Catalog.delete_catalog(catalog_id):
        print("[*] Catalog removed from database")
    else:
        print("[!] Catalog not found in database")

    print()


def handler_search(parsed: argparse.Namespace):

    query = parsed.QUERY

    table_content = [
        ["Command", "Description", "tags"]
    ]

    for cat in Catalog.search(query):
        if tags := cat["tags"]:
            tags = json.loads(tags)

        table_content.append(
            [
                cat["command"],
                cat["description"],
                ", ".join(tags)
            ]
        )

    table = SingleTable(table_content,
                        title="Found commands in catalogs")
    table.inner_row_border = True

    print("")
    print(table.table)
    print("")


def cli_catalog(parser: argparse._SubParsersAction):
    temp = parser.add_parser(
        "catalog",
        prog='mist catalog',
        description='MIST catalog manager',
        add_help=False,
    )
    temp.set_defaults(func=show_help)
    temp.add_argument('-h', '--help',
                      action="store_true",
                      help="show this help message and exit")
    temp.set_defaults(func=show_help)
    subparsers = temp.add_subparsers()

    # action -> list
    log_parser_details = subparsers.add_parser(
        "list",
        description='Displays available catalogs')
    log_parser_details.set_defaults(func=handler_list)

    # action -> ADD
    log_parser_summary = subparsers.add_parser(
        "add",
        description='Add a new catalog')
    log_parser_summary.add_argument('CATALOG_URI')
    log_parser_summary.set_defaults(func=handler_add)

    # action -> DELETE
    log_parser_console = subparsers.add_parser(
        "delete",
        description='Removes existing catalog')
    log_parser_console.add_argument('CATALOG_ID')
    log_parser_console.set_defaults(func=handler_delete)

    # action -> SEARCH
    log_parser_signatures = subparsers.add_parser(
        "search",
        description='Search in a catalog')
    log_parser_signatures.add_argument('QUERY')
    log_parser_signatures.set_defaults(func=handler_search)

    # # action -> RE-INDEX
    log_parser_signatures = subparsers.add_parser(
        "reindex",
        description='Re-index installed catalogs')
    log_parser_signatures.set_defaults(func=handler_reindex)
