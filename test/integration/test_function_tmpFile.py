import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_tmpFile.mist"

def test_print(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = execute_from_text(content)
    assert "The file is" in console
    assert "tmp" in console
    assert "/" in console
