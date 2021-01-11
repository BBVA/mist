import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "print.mist"

@pytest.mark.asyncio
async def test_print(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content, {"name": "pepe"})
    assert "hello" in console
    assert "hola adios" in console
    assert "hola pepe" in console
    assert "127.0.0.1\n" in console
    assert "The result of ping to 127.0.0.1 is True" in console
    assert "Saved result of ping to 127.0.0.1 is True" in console
    assert "myTable contains [{" in console    
