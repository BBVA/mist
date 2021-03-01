import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "basic_pipe.mist"

@pytest.mark.asyncio
async def test_basic_pipe(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)
    
    assert "Producer 1" in output
    assert "Consumer 2 : 1" in output
    assert "Producer 2" in output
    assert "Producer 3" in output
    assert "Consumer 1 : 1" in output
    assert "Consumer 1 : 2" in output
    assert "Consumer 1 : 3" in output
    assert "Producer 4" in output
    assert "Producer 5" in output
    assert "Producer 6" in output
    assert "Consumer 3 : 1" in output
    assert "Consumer 3 : 2" in output
    assert "Consumer 3 : 3" in output
    assert "Consumer 3 : 4" in output
    assert "Consumer 3 : 5" in output
    assert "Consumer 3 : 6" in output
    assert "Consumer 2 : 2" in output
    assert "Consumer 2 : 3" in output
    assert "Consumer 2 : 4" in output
    assert "Consumer 2 : 5" in output
    assert "Consumer 2 : 6" in output
    assert "Consumer 1 : 4" in output
    assert "Consumer 1 : 5" in output
    assert "Consumer 1 : 6" in output
