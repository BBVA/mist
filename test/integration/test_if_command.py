import os
import platform
import pytest

from mist.action_run import execute_from_text

CHECK_FILE = "if_command.mist"

@pytest.mark.asyncio
async def test_check_if_branch(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"index": "0"})
    assert "ONE\n" == output

@pytest.mark.asyncio
async def test_check_elsif_1_branch(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"index": "1"})
    assert "TWO\n" == output

@pytest.mark.asyncio
async def test_check_elsif_12_branch(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"index": "2"})
    assert "THREE\n" == output

@pytest.mark.asyncio
async def test_check_else_branch(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"index": "3"})
    assert "FOUR\n" == output
