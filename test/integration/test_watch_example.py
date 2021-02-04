import os
import pytest

from mist.action_run import execute_from_text

WATCH_FILE = "watch.mist"

@pytest.mark.asyncio
async def test_watch_example(examples_path):
    with open(os.path.join(examples_path, WATCH_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content)

    # assert "22\ntcp\nhola\n23\nudp\nhola\n" == console # Untin dictionaries come to Mist
    assert "23\nudp\nhola\n" == console
