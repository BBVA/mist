import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "dict2list.mist"

@pytest.mark.asyncio
async def test_dict2list(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content, waitTime=2)
    assert """[2, 1, 3]
[2, 1, 3]\n""" == console
