import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_with_named_args.mist"

@pytest.mark.asyncio
async def test_function_with_named_args(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)
    assert """[1, 2, 3]
[1, 2, 3, 4]
Peter
John
The range is [1, 2, 3]
The range is [1, 2, 3, 4]
Hello Peter
Hello John
The file is /""" in console
