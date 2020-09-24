import os

from mist.interpreter import execute_from_text

EXAMPLE_FILE = "findOpenPorts.mist"

def test_nmap_iterator_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert "\nlocalhost\nStarting Nmap" in console
    assert "\n127.0.0.1\nStarting Nmap" in console
    assert "[{'id': 1, 'Host': '127.0.0.1', 'OpenPorts':" in console
    assert ", {'id': 2, 'Host': 'localhost', 'OpenPorts':" in console

