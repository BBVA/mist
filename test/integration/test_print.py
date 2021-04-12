import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "print.mist"

@pytest.mark.asyncio
async def test_print(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content, {"name": "pepe"})
    assert """hello
hola adios
hola pepe
The result of ping to 127.0.0.1 is True
myTable contains {'ip': '127.0.0.1', 'result': True}\n""" == console
