import tempfile

from mist.sdk.config import config

def tmpFileFunction():
    if config.debug:
        print(f"-> tmpFileFunction")
    return tempfile.NamedTemporaryFile(delete=False).name

def rangeFunction(begin, end, step):
    return list(range(begin, end, step))

class _Functions(list):

    def __init__(self):
        super(_Functions, self).__init__()
        self.append({"name": "tmpFile", "native": True, "commands": tmpFileFunction})
        self.append({"name": "range", "native": True, "commands": rangeFunction})

functions = _Functions()

__all__ = ("functions", )
