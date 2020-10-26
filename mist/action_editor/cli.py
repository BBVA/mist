import argparse

from .editor import run_editor

def cli_handler(parsed_args: argparse.Namespace):
    listen_port = parsed_args.port
    listen_addr = parsed_args.listen_addr

    run_editor(listen_port, listen_addr)

def cli_editor(parser: argparse._SubParsersAction):
    run_parser = parser.add_parser('editor',
        prog='mist editor',
        description='Run live editor on browser')
    run_parser.add_argument('-p', '--port',
                            help="editor listen port (default: 9000)",
                            type=int,
                            default=9000)
    run_parser.add_argument('-l', '--listen-addr',
                            help="listen address (default: localhost)",
                            default="localhost")
    run_parser.set_defaults(func=cli_handler)
