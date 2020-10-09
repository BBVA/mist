import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "searchInJSON.mist"

def test_search_in_json_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert 'True\nTrue\nDavid\n' in console
