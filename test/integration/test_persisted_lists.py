import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "persisted_lists.mist"

@pytest.mark.asyncio
async def test_persisted_lists(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)

    assert ", 'Name': 'Letters', 'Objects': ['A', 'B']},"
    assert ", 'Name': 'Numbers', 'Objects': ['1', '2']}]"
    assert "'Name': 'Letters', 'Objects': ['A', 'B']}\n"
    assert "'Name': 'Numbers', 'Objects': ['1', '2']}\n"
    assert "['A', 'B']\n" in console
    assert "A\n" in console
    assert "B\n" in console
    assert "['1', '2']\n" in console
    assert "1\n" in console
    assert "2\n" in console


