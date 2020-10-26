import os

from mist.action_run import execute_from_text

PING_EXAMPLE_FILE = "abort.mist"

def test_abort_example(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert "Abort reached" in console
