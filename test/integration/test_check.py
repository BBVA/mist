import os
import platform

from mist.action_run import execute_from_text

CHECK_FILE = "check.mist"
CHECK_ELSE_FILE = "check_else.mist"

# For 'Linux'
paramPath = "/bin"

# For MacOSX
if (platform.system() == 'Darwin'):
    paramPath = "/usr/bin"

# Who the hell uses 'Windows'

def test_check_success(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = execute_from_text(content, {"param": f"{paramPath}/true"})
    assert "FOO\n" == output

def test_check_fail(examples_path):
    with open(os.path.join(examples_path, CHECK_FILE), "r") as f:
        content = f.read()

    output = execute_from_text(content, {"param": f"{paramPath}/false"})
    assert "" == output

def test_check_else_branch_1(examples_path):
    with open(os.path.join(examples_path, CHECK_ELSE_FILE), "r") as f:
        content = f.read()

    output = execute_from_text(content, {"param": f"{paramPath}/true"})
    assert "FOO\n" == output

def test_check_else_branch_2(examples_path):
    with open(os.path.join(examples_path, CHECK_ELSE_FILE), "r") as f:
        content = f.read()

    output = execute_from_text(content, {"param": f"{paramPath}/false"})
    assert "BAR\n" == output
