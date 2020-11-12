import os

from mist.action_run import execute_from_text

EXAMPLE_FILE_1 = "command_hello.mist"
EXAMPLE_FILE_2 = "command_with_exec_and_set.mist"

def test_hello(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE_1), "r") as f:
        content = f.read()
    
    console = execute_from_text(content)
    assert console =="""Hola Pepe
True
END
"""

def test_command_with_exec_and_set(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE_2), "r") as f:
        content = f.read()
    
    console = execute_from_text(content)
    assert console =="""127.0.0.1
INNER RESULT IS: True
OUTER RESULT IS: True
CALLER RESULT IS True
OUTPUT IS: 127.0.0.1
"""