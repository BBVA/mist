import os
import platform
import pytest
import asyncio

from mist.action_run import execute_from_text

CHECK_FILE = "pipeChainsWithAditionalParam.mist"

@pytest.mark.asyncio
async def test_wait_for_producer(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, waitTime=1)

    assert """hola 1
hola 2
hola 3\n""" == output