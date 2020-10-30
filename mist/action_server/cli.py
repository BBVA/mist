import argparse

from .server import run_server


def cli_server(parser: argparse._SubParsersAction):
    run_parser = parser.add_parser('server',
        prog='mist server',
        description='Run MIST as service')
    run_parser.add_argument('-p', '--port',
                            help="editor listen port (default: 9000)",
                            type=int,
                            default=9000)
    run_parser.add_argument('-l', '--listen-addr',
                            help="listen address (default: localhost)",
                            default="localhost")
    run_parser.add_argument('-E', '--enable-editor',
                            help="enable web based MIST editor",
                            action="store_true",
                            default=False)
    run_parser.add_argument('-R', '--redis-server',
                            required=True,
                            help="redis server for storage backend. I.e: redis://127.0.0.1:6379",
                            default=None)
    run_parser.add_argument('-c', '--concurrency',
                            help="maximum number of concurrent execution or MIST files",
                            type=int,
                            default=8)
    run_parser.set_defaults(func=run_server)
