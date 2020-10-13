import os
import re
import shutil
from collections import namedtuple

from pathlib import Path
from typing import List, Set, Tuple
from argparse import Namespace
from functools import lru_cache

from textx import metamodel_from_str

from mist.sdk import params, MistMissingBinaryException, \
    MistInputDataException

from mist.lang.classes import exports as core_exports
from mist.lang.builtin import exports as builtin_exports

from .helpers import get_or_download_mist_file
from .finders import find_catalog_exports, find_grammars, \
    extract_modules_grammar_entry

REGEX_FIND_PARAMS = re.compile(r'''(\%[\w\_\-]+)''')
HERE = os.path.dirname(__file__)


# -------------------------------------------------------------------------
# Grammar helpers
# -------------------------------------------------------------------------
def launch_hook(self):
    from mist.sdk import stack

    if results := self.run():
        if type(results) is list:

            for r in results:
                stack.append(r)

                if self.commands:
                    for c in self.commands:
                        c.launch()
                    stack.pop()

        else:

            if type(results) is dict:
                stack.append(results)

            if self.commands:
                for c in self.commands:
                    c.launch()

                if type(results) is dict:
                    stack.pop()

@lru_cache(1)
def mist_catalog_path() -> str:
    return str(Path().home().joinpath(".mist").joinpath("catalog"))

@lru_cache(1)
def get_core_grammar() -> str:
    _core_grammar = []

    for core_grammar_file in [
        os.path.join(HERE, "..", "lang", "core.tx"),
        os.path.join(HERE, "..", "lang", "builtin.tx")
    ]:
        with open(core_grammar_file, "r") as f:
            _core_grammar.append(f.read())

    return "\n".join(_core_grammar)


@lru_cache(128)
def load_catalog_grammar(path: str) -> Tuple[List[str], Set[str]]:
    """
    load grammar from a catalog path

    Returns: Tuple(Catalog Grammar as List, Modules entries as Set)
    """

    catalog_grammar = []
    modules_entries = set()
    catalog_grammar_files = find_grammars(path)
    for module_grammar_file in catalog_grammar_files:
        with open(module_grammar_file, "r") as f:
            content = f.read()

            catalog_grammar.append(content)

            # Extract catalog modules entries
            if entry := extract_modules_grammar_entry(content):
                modules_entries.add(entry)

    return catalog_grammar, modules_entries

def build_grammar(core_grammar: str,
                  modules_entries: set,
                  catalog_grammar) -> str:
    # Include catalog grammar into core grammar
    core_grammar = core_grammar.replace(
        "##MODULES##",
        " | ".join(modules_entries)
    )

    #
    # Build global grammar
    #
    return "\n".join([
        core_grammar,
        *catalog_grammar
    ])

def _find_commands_versions(mist_content,
                            modules_entries,
                            grammar,
                            base_exports) -> dict:
    """
    This command try to find specific versions specified in commands
     .mist files

     Returns dict(Command name: version)
     """

    def _build_dummy_classes(modules_entries: Set[str]) -> List[object]:
        """
        Build generic classes with 'parent', 'version' and **kwarg properties.
        """
        dummy_classes = []

        def custom_init(self, parent: str, version: str, **kwargs):
            self.parent = parent
            self.version = version
            self.__dict__.update(kwargs)

        for m in modules_entries:
            klass = type(m, (), {
                "parent": None,
                "version": None,
                "commands": []
            })

            klass.__init__ = custom_init

            dummy_classes.append(klass)

        return dummy_classes

    def _find_versions(command: List[object]) -> dict:
        meta = {}

        if type(command) is list:
            for c in command:
                if ret := _find_command_metadata(c):
                    meta.update(ret)

        if hasattr(command, "version"):
            # TODO: resolver version
            meta[command] = command.version

        try:
            for c in command.commands:
                meta.update(_find_command_metadata(c))
        except AttributeError:
            pass

        return meta


    dummy_classes = _build_dummy_classes(modules_entries)

    # Load MIST language definition
    mist_meta_model = metamodel_from_str(
        grammar,
        classes=[*base_exports, *dummy_classes],
        use_regexp_group=True
    )

    model = mist_meta_model.model_from_str(mist_content)

    versions = _find_versions(model.commands)

    del model
    del mist_meta_model
    del dummy_classes

    return versions


@lru_cache(128)
def load_mist_language(mist_file_or_content: str):

    if os.path.exists(mist_file_or_content):
        content = open(mist_file_or_content, "r").read()
    else:
        content = mist_file_or_content

    core_grammar = get_core_grammar()
    catalog_grammar, modules_entries = load_catalog_grammar(
        mist_catalog_path()
    )

    grammar = build_grammar(core_grammar, modules_entries, catalog_grammar)

    base_exports = []
    base_exports.extend(core_exports)
    base_exports.extend(builtin_exports)

    #
    # First load round.
    #
    # We need to load mist file to get user required version for
    # each command. This round will load dummy classes. The purpose of them
    # is to get the "version" property for each Command loaded.
    #
    commands_and_versions_restrictions = _find_commands_versions(
        content, modules_entries, grammar, base_exports
    )

    #
    # Locate exports
    #
    exports = [*base_exports]
    exports.extend(
        find_catalog_exports(
            mist_catalog_path(),
            modules_entries,
            commands_and_versions_restrictions
        )
    )

    #
    # Add some "magic"...
    #
    for e in exports:
        e.launch = launch_hook

    # Load MIST language definition
    mist_meta_model = metamodel_from_str(
        grammar,
        classes=exports,
        use_regexp_group=True
    )

    return mist_meta_model


# -------------------------------------------------------------------------
# Model helpers
# -------------------------------------------------------------------------
def _find_command_metadata(command: List[object]):
    meta = []

    if type(command) is list:
        for c in command:
            meta.extend(_find_command_metadata(c))

    if hasattr(command, "meta"):
        meta.append((command.__class__.__name__, command.meta))

    try:
        for c in command.commands:
            meta.extend(_find_command_metadata(c))
    except AttributeError:
        pass

    return meta


def _find_params_in_mist_file(mist_file_path: str) -> Set[str]:
    with open(mist_file_path, "r") as f:
        content = f.read()

    params = set()

    if found := REGEX_FIND_PARAMS.findall(content):
        params.update({
            x[1:] for x in found
        })

    return params


def get_mist_model(parsed_args: Namespace) \
        -> object or MistMissingBinaryException:
    """
    This function checks model, language and that all binaries are available
    """

    #
    # Check model and language
    #

    with get_or_download_mist_file(parsed_args) as mist_file:
        mist_meta_model = load_mist_language(mist_file)

        mist_model = mist_meta_model.model_from_file(
            mist_file
        )

        #
        # Check that binaries needed to execute a command are installed
        #
        if not parsed_args.no_check_tools:
            if metas := _find_command_metadata(mist_model.commands):

                for command_name, m in metas:
                    if bin := m.get("default", {}).get("cmd", None):
                        if not shutil.which(bin):
                            cmd_name = m.get("default", {}).get("name", None)
                            cmd_message = m.get("default", {}).get("cmd-message", None)
                            raise MistMissingBinaryException(
                                f"Command '{command_name}' need '{bin}' to be "
                                f"executed. Please install them. \n\nExtra "
                                f"help: {cmd_message}"
                            )

        #
        # Check that params in .mist file matches with available params
        #
        if input_params := _find_params_in_mist_file(mist_file):
            if missing_params := input_params.difference(params.keys()):
                _param_texts = "\n".join(f"- {x}" for x in missing_params)
                raise MistInputDataException(
                    f"This .mist file requires params for running. "
                    f"This params was not provided, but are necessary: \n\n"
                    f"{_param_texts}"
                    f"\n\n* REMEMBER that params are case sensitive"
                )

        return mist_model


__all__ = ("get_mist_model", "load_mist_language")
