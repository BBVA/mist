import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_as_command.mist"

@pytest.mark.asyncio
async def test_function_as_command(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)
    assert console == """[1, 2, 3]
foo
[4, 3, 2]
bar
Peter
John
"""
