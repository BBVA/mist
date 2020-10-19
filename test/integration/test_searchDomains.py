import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "searchDomains.mist"

def test_searchDomains_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content, {"domain": "germanramos.com"})

    assert "Performing Crt.sh Search Enumeration against germanramos.com" in console
