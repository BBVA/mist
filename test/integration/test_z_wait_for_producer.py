import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "wait_for_producer.mist"

@pytest.mark.asyncio
async def test_wait_for_producer(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)
    
    print("HOLA")

    assert """END
Begin sleep 3
Begin sleep 2
Begin sleep 1
End sleep 1
End sleep 2
End sleep 3\n""" == output