import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "pythonCodeAnalysis.mist"

def test_pythonCodeAnalysis_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"sourcesPath": "./mist"})

    assert "Issues detected" in console
