import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_nested.mist"

@pytest.mark.asyncio
async def test_function_nested(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)
    assert """.
.
Foo
.
.
Hello Bar
.
.
Foo2
.
.
Hello Bar2
[1, 2, 3]
My range is [1, 2, 3]
""" == console
