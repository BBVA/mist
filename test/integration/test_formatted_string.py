import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "formatted_string.mist"

def test_function_with_named_args(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)
    assert """hola
None
John
Hi None. The range is [1, 2, 3]
Again, Hi None. The range is [1, 2, 3]
""" == console
