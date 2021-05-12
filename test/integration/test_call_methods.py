import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "call_methods.mist"

@pytest.mark.asyncio
async def test_call_methods(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = await execute_from_text(content,stack=[{"MistBaseNamespace": True}])

    assert """hola Pepe
HOLA PEPE
Hola pepe
["hola", "Pepe"]
hola
["Pepe", "hola"]
{"name": "Pepe", "greeting": "hola"}
dict_keys(['name', 'greeting'])
FOO
BAR\n""" == console
