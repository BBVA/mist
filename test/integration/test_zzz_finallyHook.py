import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "finallyHook.mist"

@pytest.mark.asyncio
async def test_finally_hook(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)
    
    assert """Main end
message
My final hook 1
My final hook 2
""" == output
