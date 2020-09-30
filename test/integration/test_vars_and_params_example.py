import os

from mist.interpreter import execute_from_text

PING_EXAMPLE_FILE = "vars and params.mist"

def test_vars_and_params(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"p1": "adios"})

    assert "hola" in console
    assert "/bin" in console
    assert "adios" in console
