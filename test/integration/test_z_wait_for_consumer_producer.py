import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "wait_for_consumer_producer.mist"

@pytest.mark.asyncio
async def test_wait_for_consumer_producer(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)
    
    assert "END" in output
    assert "Begin send 1" in output
    assert "End send 1" in output
    assert "begin passNumber 1 3" in output
    assert "begin passNumber 1 1" in output
    assert "end passNumber 1 1" in output
    assert "printNumber 1" in output
    assert "end passNumber 1 3" in output
    assert "printNumber 1" in output
