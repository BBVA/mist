import os
import json
import socketserver

from typing import Tuple
from http.server import BaseHTTPRequestHandler, HTTPServer

from ..action_run import execute_from_text


class EditorServer(BaseHTTPRequestHandler):

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


def run_editor(listen_port: int, listen_addr: str):
    print(f"[*] Starting editor at port {listen_port}")
    print(f'''

    Open in your browser: http://localhost:{listen_port}

    BE CAREFUL: YOU MUST USE 'localhost' NOT '127.0.0.1'

    ''')
    httpd = HTTPServer((listen_addr, listen_port), EditorServer)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
