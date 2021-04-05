import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "indirect_pipe.mist"

@pytest.mark.asyncio
async def test_indirect_pipe(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)

    assert "hola\nhola\n" == output