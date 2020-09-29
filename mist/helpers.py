import os
import re
import importlib

from typing import Set, List
from configparser import ConfigParser

EXTRACT_MODULE_REGEX = re.compile(r'''^(.*Command)(:)''')

def find_catalog_exports(base_path: str) -> List[str]:

    def _file_to_module_(filename: str) -> str:
        m = filename.replace("/", ".")

        if m.startswith("."):
            m = m[1:]

        return m

    exports = []

    for root, dirs, files in os.walk(base_path, topdown=False):

        if "exports.py" not in files:
            continue

        meta_file = os.path.join(root, "META")

        if os.path.exists(meta_file):
            _c_parser = ConfigParser()
            _c_parser.read(filenames=meta_file)
            meta_content = _c_parser.__dict__["_sections"]
        else:
            meta_content = {}

        module_name = _file_to_module_(root.replace(base_path, ""))

        m = importlib.import_module(f"mist.commands.{module_name}.exports")

        if ex := getattr(m, "exports", None):
            #
            # Attach META Info
            #
            for e in ex:
                e.meta = meta_content

            exports.extend(ex)

    return exports


def find_grammars(base_path: str) -> Set[str]:
    """
    Search 'grammar.tx' files in catalog modules

    :return: an iterable with paths of grammars for each module found
    """


    grammar_files = set()

    for root, dirs, files in os.walk(base_path, topdown=False):
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
