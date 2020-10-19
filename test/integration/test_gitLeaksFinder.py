import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "gitLeaksFinder.mist"

def test_gitLeaksFinder_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"gitPath": "./"})

    assert "Code is clean and safe" in console
