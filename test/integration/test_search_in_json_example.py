import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "searchInJSON.mist"

@pytest.mark.asyncio
async def test_search_in_json_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)

    assert '["Pankaj", "David", "David", "Jim"]\n' in console
