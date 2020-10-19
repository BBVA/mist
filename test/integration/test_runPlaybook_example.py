import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "runPlaybook.mist"

def test_runPlaybook_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"p1": "adios"})

    assert "127.0.0.1" in console
    assert "adios" in console
