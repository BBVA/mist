import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "exec.mist"

def test_exec(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"param": "hola"})

    assert "test" in console
    assert "First exec result is True" in console
    assert "Second exec result is True and console output is hola" in console
    assert "Thrid exec result is False" in console
