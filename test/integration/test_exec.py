import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "exec.mist"

@pytest.mark.asyncio
async def test_exec(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"param": "hola"})

    assert console == """First exec result is True
hola
Second exec result is True and console output is hola
Thrid exec result is False
Last execution without commands
1
hola
2
adios
"""
