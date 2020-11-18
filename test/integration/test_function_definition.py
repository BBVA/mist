import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_definition.mist"

def test_function_definition(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = execute_from_text(content)
    assert console == "Read myfile\nAdios\n"
