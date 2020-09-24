import os

from mist.interpreter import execute_from_text

EXAMPLE_FILE = "findOpenPorts-no-iterator.mist"

def test_nmap_no_iterator_example_no_iterator(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert "Starting Nmap 7" in console
    assert "Nmap done" in console
