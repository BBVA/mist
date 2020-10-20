import os

import pytest

HERE = os.path.dirname(__file__)

@pytest.fixture(scope="function")
def examples_path() -> str:
    return os.path.abspath(os.path.join(HERE, "mist_files"))


