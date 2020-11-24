import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_as_command.mist"

def test_range(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)
    assert console == """[1, 2, 3]
foo
[4, 3, 2]
bar
Peter
John
"""
