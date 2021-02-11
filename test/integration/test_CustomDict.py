import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "customDict.mist"

@pytest.mark.asyncio
async def test_CustomDict(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)
    assert "{'first': 4, 'second': 'value'}" in console
    assert "4 value" in console
    assert "value 4" in console
    assert "{'first': 'other', 'second': 'value'}" in console
