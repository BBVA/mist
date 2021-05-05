import re
import os.path as op

from pathlib import Path
from typing import List, Set, Tuple
from functools import lru_cache

from textx import metamodel_from_str

from mist.lang.params import params
from mist.lang.exceptions import MistInputDataException, MistParseErrorException
from mist.lang.config import config
from mist.lang.herlpers import command_runner

from .helpers import get_or_download_mist_file, get_mist_filename, command_name_to_class

mist_file_base_dir = "./"

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
def get_core_grammar() -> str:
    _core_grammar = []

    for core_grammar_file in [
        op.join(HERE, "..", "lang", "core.tx"),
    ]:
        with open(core_grammar_file, "r") as f:
            _core_grammar.append(f.read())

    return "\n".join(_core_grammar)

@lru_cache(128)
def load_mist_language(mist_file_or_content: str):

    #
    # Read user .mist file
    #
    if op.exists(mist_file_or_content):
        content = open(mist_file_or_content, "r").read()
    else:
        content = mist_file_or_content

    # Load core.tx file
    grammar = get_core_grammar()

    from mist.lang.classes import exports as core_exports
    base_exports = []
    base_exports.extend(core_exports)

    #
    # Locate exports
    #
    exports = [*base_exports]

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

def check_mist_parameters(mist_file_path: str) -> None or MistInputDataException:

    if type(mist_file_path) is str and op.exists(mist_file_path):
        with open(mist_file_path, "r") as f:
            content = f.read()
        global mist_file_base_dir
        mist_file_base_dir = op.dirname(mist_file_path)
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

def get_mist_model() -> object:
    """
    This function checks model, language and that all binaries are available
    """

    with get_or_download_mist_file(get_mist_filename()) as mist_file:

        mist_meta_model = load_mist_language(mist_file)

        mist_model = mist_meta_model.model_from_file(
            mist_file
        )

        #
        # Check that params in .mist file matches with available params
        #
        check_mist_parameters(mist_file)

        return mist_model


__all__ = ("get_mist_model", "load_mist_language", "mist_file_base_dir")
