import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "wait_for_consumer.mist"

@pytest.mark.asyncio
async def test_wait_for_consumer(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)
    
    assert "END" in output
    assert "Begin sleep 3" in output
    assert "Begin sleep 2" in output
    assert "Begin sleep 1" in output
    assert "End sleep 1" in output
    assert "readNumber 1" in output
    assert "End sleep 2" in output
    assert "readNumber 2" in output
    assert "End sleep 3" in output
    assert "readNumber 3" in output
