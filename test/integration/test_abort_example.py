import os

from mist.action_run import execute_from_text
from mist.sdk.exceptions import MistAbortException

PING_EXAMPLE_FILE = "abort.mist"

def test_abort_example(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    try:  
        console = execute_from_text(content)
        assert "Abort reached" in console
    except MistAbortException:
        assert True

    
