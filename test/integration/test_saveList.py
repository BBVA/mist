import os
import pytest

from mist.action_run import execute_from_text
from mist.sdk.function import functions

MIST_FILE = "saveList.mist"

def listGeneratorFunction(kind, stack, commands):
    if kind == "dict":
        return [ {"key01": "val01", "key02": "val02"}, {"key01": "val11", "key02": "val12"} ]
    elif kind == "strList":
        return [ "val1", "val2" ]
    elif kind == "intList":
        return [ 0, 1 ]

functions["listGenerator"] = {"native": True, "commands": listGeneratorFunction}

@pytest.mark.asyncio
async def test_saveList_insert_as_is(examples_path):

    with open(os.path.join(examples_path, MIST_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"listKind": "dict", "insertType": "as_is"})
    assert "Saved key1: val01, key3: val02\nSaved key1: val11, key3: val12\n" == console

@pytest.mark.asyncio
async def test_saveList_insert_selectors_inverted(examples_path):

    with open(os.path.join(examples_path, MIST_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"listKind": "dict", "insertType": "selInv"})
    assert "Saved key1: val02, key3: val01\nSaved key1: val12, key3: val11\n" == console

@pytest.mark.asyncio
async def test_saveList_insert_selectors_and_cols_inverted(examples_path):

    with open(os.path.join(examples_path, MIST_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"listKind": "dict", "insertType": "selColInv"})
    assert "Saved key1: val01, key3: val02\nSaved key1: val11, key3: val12\n" == console

@pytest.mark.asyncio
async def test_saveList_insert_cols_inverted(examples_path):

    with open(os.path.join(examples_path, MIST_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"listKind": "dict", "insertType": "colInv"})
    assert "Saved key1: val02, key3: val01\nSaved key1: val12, key3: val11\n" == console

@pytest.mark.asyncio
async def test_saveList_insert_one_selector(examples_path):

    with open(os.path.join(examples_path, MIST_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"listKind": "dict", "insertType": "oneSel"})
    assert "Saved key1: val02, key3: None\nSaved key1: val12, key3: None\n" == console

@pytest.mark.asyncio
async def test_saveList_insert_one_selector_and_constant(examples_path):

    with open(os.path.join(examples_path, MIST_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"listKind": "dict", "insertType": "oneSelConst"})
    assert "Saved key1: val02, key3: key00\nSaved key1: val12, key3: key00\n" == console
