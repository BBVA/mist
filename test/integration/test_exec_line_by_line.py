import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "exec_line_by_line.mist"

@pytest.mark.asyncio
async def test_exec(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content,stack=[{"MistBaseNamespace": True}])

    assert '''H: requirements-doc.txt
H: requirements-test.txt
H: requirements.txt
{"result": true, "resultCode": 0,''' in console
