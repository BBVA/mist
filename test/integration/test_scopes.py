import os
import platform
import pytest

from mist.action_run import execute_from_text

CHECK_FILE = "scopes.mist"

@pytest.mark.asyncio
async def test_check_if_bool_functions(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content)

    assert """Test before - global: Global, outerLocal: Local
InnerTest before - global: test, outerLocal: Local, local: local
InnerTest after - global: innerTest, outerLocal: innerLocal, local: local
Test after - global: innerTest, outerLocal: innerLocal
Test: global: innerTest
""" == output
