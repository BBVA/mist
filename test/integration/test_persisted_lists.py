import os

from mist.action_exec import execute_from_text

EXAMPLE_FILE = "persisted lists.mist"

def test_persisted_lists(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert """[{'id': 1, 'Name': 'Letters', 'Objects': ['A', 'B']}, {'id': 2, 'Name': 'Numbers', 'Objects': ['1', '2']}]
{'id': 1, 'Name': 'Letters', 'Objects': ['A', 'B']}
['A', 'B']
A
B
{'id': 2, 'Name': 'Numbers', 'Objects': ['1', '2']}
['1', '2']
1
2
""" == console

