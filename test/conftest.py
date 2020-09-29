import os

import pytest

HERE = os.path.dirname(__file__)

@pytest.fixture(scope="function")
def examples_path() -> str:
    top_path = os.path.abspath(os.path.join(HERE, ".."))

    return os.path.join(top_path, "catalog")


