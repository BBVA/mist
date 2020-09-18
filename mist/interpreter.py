import os

from io import StringIO
from typing import Tuple
from argparse import Namespace
from functools import lru_cache

from textx import metamodel_from_str
from contextlib import redirect_stdout, redirect_stderr

from mist.sdk.db import db

from .helpers import find_grammars, find_catalog_exports, \
    extract_modules_grammar_entry
from .lang.classes import exports as core_exports
from .lang.builtin import exports as builtin_exports

@lru_cache(1)
def _load_mist_language_():

    def launch(self):
        from mist.sdk import stack

        if results := self.run():
            if type(results) is list:
                stack.extend(results)
            else:
                stack.append(results)

            if self.commands:
                for c in self.commands:
                    c.launch()
                stack.pop()

    here = os.path.dirname(__file__)
    catalog_path = os.path.join(here, "catalog")

    #
    # Locate grammars
    #

    # Locate grammar files from catalog modules
    catalog_grammar_files = find_grammars(catalog_path)

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
        find_catalog_exports(catalog_path)
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


def check(parsed_args: Namespace):
    mist_file = parsed_args.MIST_FILE

    mist_meta_model = _load_mist_language_()

    mist_model = mist_meta_model.model_from_file(
        mist_file
    )

    return mist_model

def execute(parsed_args: Namespace):
    mist_model = check(parsed_args)

    # Run user program!
    for c in mist_model.commands:
        c.launch()

def execute_from_text(text: str) -> str:
    mist_meta_model = _load_mist_language_()

    stream_stdout = StringIO()
    write_to_output = redirect_stdout(stream_stdout)

    with write_to_output:
        try:
            mist_model = mist_meta_model.model_from_str(text)

            for c in mist_model.commands:
                c.run()
        except Exception as e:
            print(f"[!] {e}", flush=True)

    # Clean database
    db.clean_database()

    return stream_stdout.getvalue()

__all__ = ("execute", "check")
