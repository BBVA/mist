import os
import pytest

from mist.action_run import execute_from_text

PING_EXAMPLE_FILE = "vars_and_params.mist"

@pytest.mark.asyncio
async def test_vars_and_params(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content, {"p1": "adios"})

    assert "hola" in console
    assert "/bin" in console
    assert "adios" in console
