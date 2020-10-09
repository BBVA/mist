import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "searchInXML.mist"

def test_search_in_xml_example(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert 'True\nTrue\nHarry Potter\n' in console
