import os
import platform
import pytest

from mist.action_run import execute_from_text

CHECK_FILE = "check.mist"
CHECK_ISNOT_FILE = "check-isnot.mist"
CHECK_ELSE_FILE = "check_else.mist"
CHECK_ELSE_ISNOT_FILE = "check_else-isnot.mist"

# For 'Linux'
paramPath = "/bin"

# For MacOSX
if (platform.system() == 'Darwin'):
    paramPath = "/usr/bin"

# Who the hell uses 'Windows'

@pytest.mark.asyncio
async def test_check_success(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/true"})
    assert "FOO\n" == output

@pytest.mark.asyncio
async def test_check_fail(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/false"})
    assert "" == output

@pytest.mark.asyncio
async def test_check_else_branch_1(examples_path):
    with open(os.path.join(examples_path, CHECK_ELSE_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/true"})
    assert "FOO\n" == output

@pytest.mark.asyncio
async def test_check_else_branch_2(examples_path):
    with open(os.path.join(examples_path, CHECK_ELSE_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/false"})
    assert "BAR\n" == output

@pytest.mark.asyncio
async def test_check_success_isnot(examples_path):
    with open(os.path.join(examples_path, CHECK_ISNOT_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/false"})
    assert "FOO\n" == output

@pytest.mark.asyncio
async def test_check_fail_isnot(examples_path):
    with open(os.path.join(examples_path, CHECK_ISNOT_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/true"})
    assert "" == output

@pytest.mark.asyncio
async def test_check_else_branch_1_ifnot(examples_path):
    with open(os.path.join(examples_path, CHECK_ELSE_ISNOT_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/false"})
    assert "FOO\n" == output

@pytest.mark.asyncio
async def test_check_else_branch_2_ifnot(examples_path):
    with open(os.path.join(examples_path, CHECK_ELSE_ISNOT_FILE), "r") as f:
        content = f.read()

    output = await execute_from_text(content, {"param": f"{paramPath}/true"})
    assert "BAR\n" == output
