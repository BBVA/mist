import os

from mist.action_exec import execute_from_text

PING_EXAMPLE_FILE = "ping.mist"

def test_ping_example(examples_path):
    with open(os.path.join(examples_path, PING_EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)

    assert "PING 127.0.0.1 (127.0.0.1): 56 data bytes" in console
    assert "[{'id': 1, 'Host': '127.0.0.1', 'Status': 'Up'}]" in console
