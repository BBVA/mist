import os

from mist.interpreter import execute_from_text

PING_EXAMPLE_FILE = "watch.mist"

def test_ping_example(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert "22\ntcp\nhola\n23\nudp\nhola\n" == console
