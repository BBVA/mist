import os
import re
import urllib
import tempfile
import importlib
import importlib.util
import urllib.request
from contextlib import contextmanager

from typing import Set, List
from configparser import ConfigParser

import argparse

EXTRACT_MODULE_REGEX = re.compile(r'''^(.*Command)(:)''')


def load_cli_exec_values(d, parsed: argparse.Namespace):
    if len(parsed.OPTIONS) > 1:

        for _tuple in parsed.OPTIONS[1:]:
            k, v = _tuple.split("=")
            d[k] = v


@contextmanager
def get_or_download_mist_file(parsed_args):
    mist_file = parsed_args.OPTIONS[0]

    if mist_file.startswith("http"):
        with tempfile.NamedTemporaryFile(prefix="mist-download") as f:
            with urllib.request.urlopen(mist_file) as remote:
                f.write(remote.read())
                f.flush()

            yield f.name

    else:
        yield mist_file

__all__ = ("get_or_download_mist_file", )
