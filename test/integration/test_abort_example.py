import os
import pytest

from mist.action_run import execute_from_text
from mist.lang.exceptions import MistAbortException

PING_EXAMPLE_FILE = "abort.mist"

@pytest.mark.asyncio
async def test_abort_example(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    try:  
        console = await execute_from_text(content)
        assert "Abort reached" in console
    except MistAbortException:
        assert True

    
