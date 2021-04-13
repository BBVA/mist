import argparse

from mist.lang.config import config
from mist.lang.params import params
from mist.lang.exceptions import MistMissingBinaryException, MistInputDataException, MistAbortException, MistUndefinedVariableException

from .interpreter import execute
from .helpers import load_cli_exec_values


def cli_handler(parsed_args: argparse.Namespace):
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
    except MistUndefinedVariableException as e:
        print()
        print("[!] Undefined variable: " + str(e))
        print()

    except MistAbortException as e:
        ex_len = len(str(e))
        ex_step1 = int(ex_len / 2) - 4

        if ex_len % 2 != 0:
            ex_step2 = ex_step1 + 2
        else:
            ex_step2 = ex_step1 + 1

        print("!" * (ex_len + 4))
        print("!", " " * ex_step1, "ABORT", " " * ex_step2, "!")
        print("!", " " * ex_len, "!")
        print("!", e, "!")
        print("!", " " * ex_len, "!")
        print("!" * (ex_len + 4))

        exit(1)
    except KeyboardInterrupt:
        print()
        print("[*] Closing session")
        print()

def cli_run(parser: argparse._SubParsersAction):
    run_parser = parser.add_parser('run',
        prog='mist run',
        description='execute a .mist file',
        usage='''%(prog)s [-h] [-N] [-C] [-R] [-d] [-S] [-p] IST_FILE [PARAMS ...]

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
    ''',
        add_help=False)
    run_parser.add_argument('OPTIONS',
                            help="MIST - FILE[param1 = value1 param2 = value2...]",
                            metavar="OPTIONS", nargs="+")
    run_parser.add_argument('-N', '--no-check-tools',
                            action="store_true",
                            help="do not check if tools are installed",
                            default=False)
    run_parser.add_argument('-C', '--console-output',
                            action="store_false",
                            help="displays console output of executed tools",
                            default=True)
    run_parser.add_argument('-R', '--real-time',
                            action="store_false",
                            help="display console output in real time",
                            default=True)
    run_parser.add_argument('-d', '--debug',
                            action="store_true",
                            help="enable debug messages",
                            default=False)
    run_parser.add_argument('-S', '--simulate',
                            action="store_true",
                            help="simulate without execute",
                            default=False)
    run_parser.set_defaults(func=cli_handler)
