import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "set.mist"

def test_set(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = execute_from_text(content)
    assert console =="""Simon says Hello
Goodbye
Simon says Hello again
Hey
Simon says Hello again and again
Simon says Hey
Simon says Bye
Simon says Hey
"""