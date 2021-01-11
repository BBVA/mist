import os
import pytest

from mist.action_run import execute_from_text

PING_EXAMPLE_FILE = "csv.mist"

@pytest.mark.asyncio
async def test_csv_example(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)

    assert ", 'ip': '127.0.0.1', 'so': 'windows', 'status': 'up'}, {'id': '" in console
    assert ", 'ip': 'localhost', 'so': 'linux', 'status': 'up'}]" in console
