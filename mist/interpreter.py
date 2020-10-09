import os
import re
import shutil
import tempfile
import urllib.request

from io import StringIO
from typing import List, Set
from argparse import Namespace
from functools import lru_cache

from textx import metamodel_from_str
from contextlib import redirect_stdout, contextmanager

from mist.sdk import db, params, MistMissingBinaryException, MistInputDataException

from .helpers import find_grammars, find_catalog_exports, \
    extract_modules_grammar_entry
from .lang.classes import exports as core_exports
from .lang.builtin import exports as builtin_exports
from .sdk import config

REGEX_FIND_PARAMS = re.compile(r'''(\%[\w\_\-]+)''')

@lru_cache(1)
def _load_mist_language_():

    def launch(self):
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

    here = os.path.dirname(__file__)
    commands_path = os.path.join(here, "catalog")

    #
    # Locate grammars
    #

    # Locate grammar files from catalog modules
    catalog_grammar_files = find_grammars(commands_path)

    # Locate core grammar files
    core_grammar_files = [
        os.path.join(here, "lang", "core.tx"),
        os.path.join(here, "lang", "builtin.tx")
    ]

    core_grammars_builder = []

    for core_grammar_file in core_grammar_files:
        with open(core_grammar_file, "r") as f:
            core_grammars_builder.append(f.read())

    core_grammar = "\n".join(core_grammars_builder)

    modules_entries = set()
    catalog_grammars_builder = []

    for module_grammar_file in catalog_grammar_files:
        with open(module_grammar_file, "r") as f:
            content = f.read()

            catalog_grammars_builder.append(content)

            # Extract catalog modules entries
            if entry := extract_modules_grammar_entry(content):
                modules_entries.add(entry)

    # Add Modules to core grammar
    core_grammar = core_grammar.replace(
        "##MODULES##",
        " | ".join(modules_entries)
    )

    grammar = "\n".join([
        core_grammar,
        *catalog_grammars_builder
    ])

    #
    # Locate exports
    #
    exports = []
    exports.extend(core_exports)
    exports.extend(builtin_exports)
    exports.extend(
        find_catalog_exports(commands_path)
    )

    #
    # Add some "magic"...
    #
    for e in exports:
        e.launch = launch

    # Load MIST language definition
    mist_meta_model = metamodel_from_str(
        grammar,
        classes=exports,
        use_regexp_group=True
    )

    return mist_meta_model

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


def check(parsed_args: Namespace) \
        -> object or MistMissingBinaryException:
    """
    This function checks model, language and that all binaries are available
    """

    #
    # Check model and language
    #

    with get_or_download_mist_file(parsed_args) as mist_file:
        mist_meta_model = _load_mist_language_()

        mist_model = mist_meta_model.model_from_file(
            mist_file
        )

        #
        # Check binaries
        #
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

def execute(parsed_args: Namespace):
    mist_model = check(parsed_args)

    if parsed_args.simulate:
        print("[*] File loaded successfully")
    else:
        # Run user program!
        for c in mist_model.commands:
            c.launch()

def execute_from_text(text: str, fn_params: dict = None) -> str:
    if fn_params:
        params.update(fn_params)

    # Set config defaults
    config.update({
        "console_output": True,
        "real_time": True,
        "debug": False,
        "persist": False,
        "database_path": None,
        "simulate": False,
        "no_check_tools": False
    })

    mist_meta_model = _load_mist_language_()

    stream_stdout = StringIO()
    write_to_output = redirect_stdout(stream_stdout)

    with write_to_output:
        try:
            mist_model = mist_meta_model.model_from_str(text)

            for c in mist_model.commands:
                c.launch()
        except Exception as e:
            print(f"[!] {e}", flush=True)

    # Clean database
    db.clean_database()

    return stream_stdout.getvalue()

__all__ = ("execute", "check")
