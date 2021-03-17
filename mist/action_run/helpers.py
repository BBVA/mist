import os
import re
import urllib
import tempfile
import importlib
import importlib.util
import urllib.request
from contextlib import contextmanager
from functools import lru_cache

from typing import Set, List
from configparser import ConfigParser

import argparse

from mist.lang.config import config

EXTRACT_MODULE_REGEX = re.compile(r'''^(.*Command)(:)''')


def load_cli_exec_values(d, parsed: argparse.Namespace):
    if len(parsed.OPTIONS) > 1:

        for _tuple in parsed.OPTIONS[1:]:
            k, v = _tuple.split("=")
            d[k] = v


@contextmanager
def get_or_download_mist_file(mist_file):

    if mist_file.startswith("http"):
        with tempfile.NamedTemporaryFile(prefix="mist-download") as f:
            with urllib.request.urlopen(mist_file) as remote:
                f.write(remote.read())
                f.flush()

            yield f.name

    else:
        yield mist_file


@lru_cache
def get_mist_filename() -> str:
    """Get MIST file from mist exec command"""
    return config.OPTIONS[0]


def command_name_to_class(name: str) -> str:
    """
    This function transform command name, from INDEX file, to MIST
    "compilant" name
    """
    return f"{name[0].upper()}{name[1:]}Command"


__all__ = ("get_or_download_mist_file", )
