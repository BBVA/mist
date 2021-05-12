import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "filterDict_pipe.mist"

@pytest.mark.asyncio
async def test_filterDictPipe(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content, waitTime=1)
    assert '''{"a": 1, "b": 2}
{"a": 1}\n''' == console
