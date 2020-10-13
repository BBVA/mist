import os
import re
import importlib
import importlib.util
from functools import lru_cache

from typing import Set, List, Tuple
from configparser import ConfigParser

EXTRACT_MODULE_REGEX = re.compile(r'''^(.*Command)(:)''')


# -------------------------------------------------------------------------
# Catalog exports helpers
# -------------------------------------------------------------------------
@lru_cache(200)
def _file_to_module_(filename: str) -> str:
    m = filename.replace("/", ".")

    if m.startswith("."):
        m = m[1:]

    return m

def _ensure_class_is_command(cmd_obj, modules_entries: Set) -> bool:
    """This function perform some _load_mist_model_ for each python class found, for
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

def _validate_index(index_path: str) -> None or dict:
    _c_parser = ConfigParser()
    _c_parser.read(filenames=index_path)
    index_content = _c_parser.__dict__["_sections"]

    if not "MIST-INDEX" in index_content:
        return None

    index_mist = index_content["MIST-INDEX"]

    if not all(x in index_mist for x in (
            "name", "description", "tags", "latest"
    )):
        return None

    return index_mist

def _validate_meta(meta_path: str) -> None or dict:
    _c_parser = ConfigParser()
    _c_parser.read(filenames=meta_path)
    meta_content = _c_parser.__dict__["_sections"]

    if not "default" in meta_content:
        return None

    meta_default = meta_content["default"]

    if not all(x in meta_default for x in (
            "version", "cmd", "cmd-message"
    )):
        return None

    return meta_default

def _find_command_version(base_path: str,
                          modules_entries: set,
                          latest_version: str,
                          restrictions: dict) \
        -> None or object:

    for root, dirs, files in os.walk(base_path,
                                     topdown=False,
                                     followlinks=True):

        if "META" not in files or "exports.py" not in files:
            continue

        meta_file = os.path.join(root, "META")

        if not (meta_content := _validate_meta(meta_file)):
            continue

        #
        # Load command at this path
        #
        module_name = _file_to_module_(
            root.replace(os.path.join(root, "exports.py") , "")
        )
        module_path = os.path.join(root, "exports.py")

        spec = importlib.util.spec_from_file_location(
            module_name,
            module_path
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # Not forget this line!

        if ex := getattr(m, "exports", None):

            for klass in ex:

                if not _ensure_class_is_command(klass, modules_entries):
                    continue

                # Ensure command loaded command is the correct version
                if not (klass_version := restrictions.get(klass, None)):
                    klass_version = latest_version

                if klass_version != meta_content["version"]:
                    continue

                klass.meta = meta_content

                return klass


def find_catalog_exports_(path: str,
                         modules_entries: Set[str],
                         restrictions: dict = None) -> List[str]:


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
        spec.loader.exec_module(m)  # Not forget this line!

        if ex := getattr(m, "exports", None):
            #
            # Attach META Info
            #
            for klass in ex:

                if not _ensure_class_is_command(klass):
                    continue

                klass.meta = meta_content

                exports.append(klass)

    return exports

def find_catalog_exports(path: str,
                         modules_entries: Set[str],
                         restrictions: dict = None) -> List[str]:


    exports = []

    for root, dirs, files in os.walk(path, topdown=False, followlinks=True):

        if "INDEX" not in files:
            continue

        # Finding INDEX command package
        index_file = os.path.join(root, "INDEX")

        if not (index_content := _validate_index(index_file)):
            continue

        # Finding command set by user
        if klass := _find_command_version(
                root,
                modules_entries,
                index_content["latest"],
                restrictions
            ):

            exports.append(klass)
        continue

        command_path = os.path.join(root, cmd_path)

        if "exports.py" not in os.listdir(command_path):
            continue

        module_name = _file_to_module_(root.replace(path, ""))
        module_path = os.path.join(root, "exports.py")

        spec = importlib.util.spec_from_file_location(
            module_name,
            module_path
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # Not forget this line!

        if ex := getattr(m, "exports", None):
            #
            # Attach META Info
            #
            for klass in ex:

                if not _ensure_class_is_command(klass, modules_entries):
                    continue

                klass.meta = cmd_meta

                exports.append(klass)

    return exports


def find_grammars(path: str) -> Set[str]:
    """
    Search 'grammar.tx' files in catalog modules

    :return: an iterable with paths of grammars for each module found
    """


    grammar_files = set()

    for root, dirs, files in os.walk(path, topdown=False, followlinks=True):
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
           "find_catalog_exports", )
