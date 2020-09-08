import os

from argparse import Namespace
from textx import metamodel_from_str

from .helpers import find_grammars, find_catalog_exports, \
    extract_modules_grammar_entry
from .lang.classes import exports as core_exports
from .lang.exec import exports as exec_exports

def _load_mist_language_():

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
    exports.extend(exec_exports)
    exports.extend(
        find_catalog_exports(catalog_path)
    )

    open("grammar.tx", "w").write(grammar)

    # Load MIST language definition
    mist_meta_model = metamodel_from_str(
        grammar,
        classes=exports
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
        c.run()


__all__ = ("execute", "check")
