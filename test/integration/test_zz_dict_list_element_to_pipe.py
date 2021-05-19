import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "dict_list_element_to_pipe.mist"

@pytest.mark.asyncio
async def test_dict_list_element_to_pipe(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content, waitTime=1)
    assert console.count('3') == 3
    assert console.count('2') == 3
    assert console.count('c') == 3
