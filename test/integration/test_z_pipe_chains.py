import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "pipeChains.mist"

@pytest.mark.asyncio
async def test_wait_for_producer(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)

    assert """Direct parameter
Direct value
Value from variable
Value from pipe
ExplicitQueue to parameter queue
ExplicitQueue to parameter queue
Implicit queue
Implicit queue
Direct value to function and explicit queue
Send and old pipe notation
Send and new pipe notation
Chain of 3 with explicit pipes
Chain of 3 with explicit pipes
Chain of 4 with explicit pipes
Chain of 4 with explicit pipes
Chain of 4 with explicit pipes
Implicit pipe of 2
Implicit pipe of 2
Implicit pipe of 3
Implicit pipe of 3
Implicit pipe of 3\n""" == output