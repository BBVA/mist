import re
import shutil
import os.path as op

from pathlib import Path
from typing import List, Set, Tuple
from functools import lru_cache

from textx import metamodel_from_str

from mist.sdk import params, MistMissingBinaryException, \
    MistInputDataException, config, db, MistParseErrorException, command_runner

from mist.lang.classes import exports as core_exports

from .helpers import get_or_download_mist_file, get_mist_filename, command_name_to_class
from .loaders import find_catalog_exports, find_grammars, \
    extract_modules_grammar_entry
from ..finders import find_commands_folders, find_catalog_metas

REGEX_FIND_PARAMS = re.compile(r'''(\%[\w\_\-]+)''')
HERE = op.dirname(__file__)
GRAMMAR_TEMPLATE = """
##COMMAND_CLASS##:
  '##COMMAND##' args*=IDorSTRING[eolterm] ('{'
    ('version' '<=' version=STRING)?
    ('input' '{'
      params+=Param
    '}')?
    ('output' '{'
      outputs+=OutputId
    '}')?
    ('then' '{'
      commands+=Command
    '}')?
  '}')?
;

"""

# -------------------------------------------------------------------------
# Grammar helpers
# -------------------------------------------------------------------------
async def launch_hook(self, stack):
    results = await self.run(stack)
    return results

@lru_cache(1)
def mist_catalog_path() -> str:
    return str(Path().home().joinpath(".mist").joinpath("catalog"))

@lru_cache(1)
def get_core_grammar() -> str:
    _core_grammar = []

    for core_grammar_file in [
        op.join(HERE, "..", "lang", "core.tx"),
    ]:
        with open(core_grammar_file, "r") as f:
            _core_grammar.append(f.read())

    return "\n".join(_core_grammar)


@lru_cache(128)
def load_catalog(path: str) -> Tuple[List[str], List[str]]:
    """
    This function walk catalog and try to discover Catalog commands Classes
    definitions and their .tx (grammar file)

    Returns: Tuple(Catalog Grammar as List, Modules entries as Set)
    """

    catalog_grammar = []

    # This must be a list because order is very important!
    modules_entries = []

    for (command_path, index_content) in find_commands_folders(path):

        #
        # If command defines their own grammar then load it
        #
        grammar_file = op.join(command_path, "grammar.tx")
        if op.exists(grammar_file):
            with open(grammar_file, "r") as f:
                content = f.read()
                catalog_grammar.append(content)

                # Extract Command name from grammar
                if entry := extract_modules_grammar_entry(content):
                    if entry not in modules_entries:
                        modules_entries.append(entry)

        else:

            command_name = index_content["name"]
            command_class = command_name_to_class(command_name)
            #
            # Otherwise use grammar template and and INDEX meta data to build
            # an on-the-fly grammar
            #
            on_the_fly_grammar = GRAMMAR_TEMPLATE.replace(
                "##COMMAND_CLASS##",
                command_class
            ).replace(
                "##COMMAND##",
                command_name
            )

            catalog_grammar.append(on_the_fly_grammar)
            modules_entries.append(command_class)

    return catalog_grammar, modules_entries

def build_grammar(core_grammar: str,
                  modules_entries: list,
                  catalog_grammar) -> str:
    # Include catalog grammar into core grammar
    core_grammar = core_grammar.replace(
        "##MODULES##", " | ".join(modules_entries)
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
                if ret := _find_versions(c):
                    meta.update(ret)

        elif cmd_version := getattr(command, "version", None):
            # TODO: resolver version
            meta[command.__class__.__name__] = cmd_version

        try:
            for c in command.commands:
                meta.update(_find_versions(c))
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

    try:
        model = mist_meta_model.model_from_str(mist_content)
    except Exception as e:
        raise MistParseErrorException(str(e))

    versions = _find_versions(model.commands)

    del model
    del mist_meta_model
    del dummy_classes

    return versions


@lru_cache(128)
def load_mist_language(mist_file_or_content: str):

    #
    # Read user .mist file
    #
    if op.exists(mist_file_or_content):
        content = open(mist_file_or_content, "r").read()
    else:
        content = mist_file_or_content

    # Load core.tx and buildin.tx files
    core_grammar = get_core_grammar()

    catalog_grammar, modules_entries = load_catalog(
        mist_catalog_path()
    )

    grammar = build_grammar(core_grammar, modules_entries, catalog_grammar)
    # grammar = catalog_grammar

    base_exports = []
    base_exports.extend(core_exports)

    # TODO: REMOVE CATALOG
    #
    # First load round.
    #
    # We need to load mist file to get user required version for
    # each command. This round will load dummy classes. The purpose of them
    # is to get the "version" property for each Command loaded.
    #
    # commands_and_versions_restrictions = _find_commands_versions(
    #     content, modules_entries, grammar, base_exports
    # )

    #
    # Locate exports
    #
    exports = [*base_exports]

    # TODO: REMOVE CATALOG
    # exports.extend(
    #     find_catalog_exports(
    #         mist_catalog_path(),
    #         modules_entries,
    #         commands_and_versions_restrictions
    #     )
    # )

    #
    # Add some "magic"...
    #
    for e in exports:
        e.launch = launch_hook

    # Load MIST language definition
    # open("grammar.tx", "w").write(grammar)
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


def check_mist_parameters(mist_file_path: str) -> None or MistInputDataException:

    if type(mist_file_path) is str and op.exists(mist_file_path):
        with open(mist_file_path, "r") as f:
            content = f.read()
    else:
        content = mist_file_path

    input_params = set()

    if found := REGEX_FIND_PARAMS.findall(content):
        input_params.update({
            x[1:] for x in found
        })

    if missing_params := input_params - set(params.keys()):
        _param_texts = "\n".join(f"- {x}" for x in missing_params)
        raise MistInputDataException(
            f"This .mist file requires params for running. "
            f"This params was not provided, but are necessary: \n\n"
            f"{_param_texts}"
            f"\n\n* REMEMBER that params are case sensitive"
        )


def check_installed_binaries(mist_model) -> None or MistMissingBinaryException:
    if metas := _find_command_metadata(mist_model.commands):

        for command_name, m in metas:
            if bin := m.get("default", {}).get("cmd", None):
                if not shutil.which(bin):
                    cmd_name = m.get("default", {}).get("name", None)
                    cmd_message = m.get("default", {}).get("cmd-error", None)
                    raise MistMissingBinaryException(
                        f"Command '{command_name}' need '{bin}' to be "
                        f"executed. Please install them. \n\nExtra "
                        f"help: {cmd_message}"
                    )


def get_mist_model() \
        -> object or MistMissingBinaryException:
    """
    This function checks model, language and that all binaries are available
    """

    def store_file_in_db(mist_file: str):
        mist_content = open(mist_file, "r").read()

        db.create_table("mist_file", ("file_name", "file_content"))
        db.insert("mist_file", (mist_file, mist_content))

    with get_or_download_mist_file(get_mist_filename()) as mist_file:

        # Store mist content in database
        store_file_in_db(mist_file)

        mist_meta_model = load_mist_language(mist_file)

        mist_model = mist_meta_model.model_from_file(
            mist_file
        )

        #
        # Check that binaries needed to execute a command are installed
        #
        # if not config.no_check_tools:
        #     check_installed_binaries(mist_model)

        #
        # Check that params in .mist file matches with available params
        #
        check_mist_parameters(mist_file)

        return mist_model


__all__ = ("get_mist_model", "load_mist_language")
