import os
import re
import urllib
import pathlib
import importlib
import importlib.util
import urllib.request

from typing import Set, List
from configparser import ConfigParser

EXTRACT_MODULE_REGEX = re.compile(r'''^(.*Command)(:)''')

def find_catalog_exports(path: str, modules_entries: Set[str]) -> List[str]:

    def _file_to_module_(filename: str) -> str:
        m = filename.replace("/", ".")

        if m.startswith("."):
            m = m[1:]

        return m

    def _ensure_command_checks(cmd_obj) -> bool:
        """This function perform some check for each python class found, for
        ensuring that a command has all needs"""

        # A command must be in Modules entries
        if cmd_obj.__name__ not in modules_entries:
            return False

        #
        # A command must has 1 property and 1 methods
        #

        # Only dataclasses
        if hasattr(cmd_obj, "__annotations__"):
            if "parent" not in cmd_obj.__annotations__:
                return False
        elif not hasattr(cmd_obj, "parent"):
            return False

        if not hasattr(cmd_obj, "run"):
            return False

        return True

    exports = []

    for root, dirs, files in os.walk(path, topdown=False):

        if "exports.py" not in files:
            continue

        meta_file = os.path.join(root, "META")

        if os.path.exists(meta_file):
            _c_parser = ConfigParser()
            _c_parser.read(filenames=meta_file)
            meta_content = _c_parser.__dict__["_sections"]
        else:
            meta_content = {}

        module_name = _file_to_module_(root.replace(path, ""))
        module_path = os.path.join(root, "exports.py")

        spec = importlib.util.spec_from_file_location(
            module_name,
            module_path
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)

        if ex := getattr(m, "exports", None):
            #
            # Attach META Info
            #
            for klass in ex:

                if not _ensure_command_checks(klass):
                    continue

                klass.meta = meta_content

                exports.append(klass)

    return exports


def find_grammars(path: str) -> Set[str]:
    """
    Search 'grammar.tx' files in catalog modules

    :return: an iterable with paths of grammars for each module found
    """


    grammar_files = set()

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:

            if not name.endswith(".tx"):
                continue

            grammar_files.add(
                os.path.abspath(os.path.join(root, name))
            )

    return grammar_files

def extract_modules_grammar_entry(text: str) -> str or None:
    if found := EXTRACT_MODULE_REGEX.search(text):
        return found.group(1)
    else:
        return None

__all__ = ("find_grammars", "extract_modules_grammar_entry",
           "find_catalog_exports")
