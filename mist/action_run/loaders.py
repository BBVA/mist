import os
import re
import importlib
import os.path as op
import importlib.util

from typing import Set, List
from functools import lru_cache

from mist.sdk import MistInputDataException
from mist.finders import find_commands_folders

from .helpers import command_name_to_class
from ..action_catalog import Catalog

EXTRACT_MODULE_REGEX = re.compile(r'''^(.*Command)(:)''')


# -------------------------------------------------------------------------
# Catalog exports helpers
# -------------------------------------------------------------------------
@lru_cache(200)
def _file_to_module_(filename: str) -> str:
    m = filename.replace("/", ".").replace("-", "_")

    if m.startswith("."):
        m = m[1:]

    return m

def _ensure_class_is_command(cmd_obj, modules_entries: Set) -> bool:
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


def _find_command_version(base_path: str,
                          modules_entries: set,
                          index_content: dict,
                          restrictions: dict) \
        -> None or object:

    command_name = index_content["name"]

    if command_name in restrictions:
        command_version = restrictions[command_name]
    else:
        command_version = index_content["latest"]

    #
    # Find location of command implementation
    #
    if not(location := Catalog.find_command(command_name, command_version)):
        raise MistInputDataException(
            f"Error while loading catalog commands. "
            f"Can't find command '{command_name}' with "
            f"version '{command_version}'. "
            f"Try to fix then re-indexing them writing: mist catalog reindex"
        )

    #
    # Load command at this path
    #
    module_path = op.join(location["command_path"], "exports.py")
    module_name = _file_to_module_(
        module_path.replace(op.sep.join(base_path.split(op.sep)[:-1]), "")
    )

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

            klass.meta = index_content

            return klass


def find_catalog_exports(path: str,
                         modules_entries: List[str],
                         restrictions: dict = None) -> List[str]:


    exports = []

    for (command_path, index_content) in find_commands_folders(path):

        # Finding command set by user
        if klass := _find_command_version(
                command_path,
                modules_entries,
                index_content,
                restrictions
            ):

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
                op.abspath(op.join(root, name))
            )

    return grammar_files

def extract_modules_grammar_entry(text: str) -> str or None:
    if found := EXTRACT_MODULE_REGEX.search(text):
        return found.group(1)
    else:
        return None


__all__ = ("find_grammars", "extract_modules_grammar_entry",
           "find_catalog_exports", )
