import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "list_functions.mist"

@pytest.mark.asyncio
async def test_list_functions(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)
    results = console.split("\n")
    assert "Length = 3" == results[0]
    assert "Cleared = []" == results[1]
    assert 'Sorted = ["four", "one", "three", "two"]' == results[2]
    assert 'Reversed = ["two", "three", "one", "four"]' == results[3]
    assert 'Appended = ["two", "three", "one", "four", "five"]' == results[4]
    assert 'Removed = ["three", "one", "four", "five"]' == results[5]
