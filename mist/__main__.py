import os
import sys
import json
import argparse
import platform
import socketserver
import pkg_resources

from typing import Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler

from mist.sdk import config, db

from .interpreter import execute, check, execute_from_text

HERE = os.path.dirname(__file__)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int],
                 server: socketserver.BaseServer):
        assets_base = os.path.join(os.path.dirname(__file__), "assets")
        self.assets_index = os.path.join(assets_base, "index.html")
        self.assets_js = os.path.join(assets_base, "mode-mist.js")

        super().__init__(request, client_address, server)

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        if self.path == "/mode-mist.js":
            with open(self.assets_js, "rb") as f:
                self.wfile.write(f.read())

        else:
            with open(self.assets_index, "rb") as f:
                self.wfile.write(f.read())


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        program = self.rfile.read(content_length)

        stdout = execute_from_text(program.decode("utf-8"))

        response = json.dumps({"console": stdout})

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))



class Mist(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='MIST - programing language for security made easy',
            usage='''mist <command> [<args>]

Available commands are:
   version    Displays installed MIST version
   exec       Run a .mist file (default option)
   check      Check a .mist file without execute them
   editor     Run live editor on browser
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

    def editor(self):

        print("[*] Starting editor at port 9000")
        print('''

        Open in your browser: http://localhot:9000
        
        BE CAREFUL: YOU MUST USE 'localhost' NOT '127.0.0.1'
        
        ''')
        httpd = HTTPServer(('localhost', 9000), SimpleHTTPRequestHandler)
        httpd.serve_forever()

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
