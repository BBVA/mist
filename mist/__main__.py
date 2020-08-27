import os
import argparse
import platform
import pkg_resources

import textx

class MistException(Exception):
    pass

def execute(parsed: argparse.Namespace):
    # check if input file exits
    mist_file = parsed.MIST_FILE

    if not os.path.exists(mist_file):
        raise MistException(f"File '{mist_file}' doesn't exits")

    here = os.path.dirname(__file__)

    model_file = os.path.join(here, "models", "mist.tx")
    mist_model = textx.metamodel_from_file(model_file)


    #
    # TODO
    #
    # hacking_model = mist_model.model_from_file(mist_file)
    # interpret(hacking_model)

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

    parser = argparse.ArgumentParser(
        description='MIST - programing language for security made easy'
    )

    parser.add_argument("MIST_FILE")
    parser.add_argument("--version",
                        action="store_true",
                        default=False,
                        help="show version")

    parsed = parser.parse_args()

    if parsed.version:
        print(f"version: {pkg_resources.get_distribution('mist').version}")
        print()
        exit()

    try:
        execute(parsed)
    except MistException as e:
        print(f"[!] {e}")
        exit(1)


if __name__ == '__main__':
    main()
