import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_with_named_args.mist"

def test_function_with_named_args(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)
    assert """[1, 2, 3]
[1, 2, 3, 4]
Peter
John
The range is [1, 2, 3]
The range is [1, 2, 3, 4]
The file is /""" in console
