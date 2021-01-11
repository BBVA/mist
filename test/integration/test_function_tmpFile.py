import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_tmpFile.mist"

@pytest.mark.asyncio
async def test_tmpFile(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content)
    assert "The file is" in console
    assert "tmp" in console
    assert "/" in console
