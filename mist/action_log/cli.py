import argparse

from .actions import log_console, log_summary, log_details, log_signature

def show_help(args):
    print('''usage: mist log <command> [<args>]

Available commands:
   summary     Displays executions summary
   details     Display details for specific register
   console     Displays console execution for a register
   signatures  Checks database and console output signatures
   help        Displays help menu

MIST Log manager

optional arguments:
  -h, --help            show this help message and exit
''')

def cli_log(parser: argparse._SubParsersAction):
    temp = parser.add_parser(
        "log",
        prog='mist log',
        description='MIST Log manager',
        add_help=False,
    )
    temp.set_defaults(func=show_help)
    temp.add_argument('-h', '--help',
                      action="store_true",
                      help="show this help message and exit")
    temp.set_defaults(func=show_help)
    subparsers = temp.add_subparsers()

    # action -> DETAILS
    log_parser_details = subparsers.add_parser(
        "details",
        description='Displays executions summary')
    log_parser_details.add_argument('MIST_DB')
    log_parser_details.add_argument('-i', '--row-id',
                        required=True,
                        help="register ID which get details")
    log_parser_details.set_defaults(func=log_details)

    # action -> SUMMARY
    log_parser_summary = subparsers.add_parser(
        "summary",
        description='Displays executions summary')
    log_parser_summary.add_argument('MIST_DB')
    log_parser_summary.set_defaults(func=log_summary)

    # action -> CONSOLE
    log_parser_console = subparsers.add_parser(
        "console",
        description='Displays executions consoled for a execution')
    log_parser_console.add_argument('MIST_DB')
    log_parser_console.add_argument('-i', '--row-id',
                        required=True,
                        help="register ID which get details")
    log_parser_console.set_defaults(func=log_console)

    # action -> SIGNATURES
    log_parser_signatures = subparsers.add_parser(
        "signatures",
        description='Checks console and database signatures')
    log_parser_signatures.add_argument('MIST_DB')
    log_parser_signatures.add_argument('-s', '--signature-file',
                        default=None,
                        help="signature file. usuallyy with .db.signature")
    log_parser_signatures.add_argument('-q', '--quiet',
                        action="store_true",
                        default=False,
                        help="hide log. Only summary message")

    log_parser_signatures.set_defaults(func=log_signature)
