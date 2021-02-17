import os
import platform
import pytest

from mist.action_run import execute_from_text

CHECK_FILE = "bool_func_if.mist"

@pytest.mark.asyncio
async def test_check_if_bool_functions(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content)

    assert "NOT IF\nAND ELSE\nOR IF\n" == output
