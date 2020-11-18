import tempfile

from mist.sdk.config import config

def tmpFileFunction():
    if config.debug:
        print(f"-> tmpFileFunction")
    return tempfile.NamedTemporaryFile(delete=False).name

class _Functions(list):

    def __init__(self):
        super(_Functions, self).__init__()
        self.append({"name": "tmpFile", "native": True, "commands": tmpFileFunction})

functions = _Functions()

__all__ = ("functions", )
