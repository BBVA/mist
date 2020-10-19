import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "searchOpenS3Buckets.mist"

def test_searchOpenS3Buckets_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"domain": "germanramos.com"})

    assert "Starting FestIN" in console
