import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_range.mist"

@pytest.mark.asyncio
async def test_range(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)
    assert "[1, 2, 3]" in console
