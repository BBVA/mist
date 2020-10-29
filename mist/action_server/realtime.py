import argparse

from flask import Flask
from flask_sse import sse


def setup_realtime(_app: Flask, parsed_args: argparse.Namespace):

    redis_server = parsed_args.redis_server

    if not redis_server:
        print()
        print("[!] Can't enable realtime update in IDE without enabling"
              " Redis backend. Option '-E'")
        print()

        return

    _app.config["REDIS_URL"] = redis_server
    _app.register_blueprint(sse, url_prefix='/stream')

