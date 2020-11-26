import tempfile
import re

from mist.sdk.config import config

def tmpFileFunction():
    return tempfile.NamedTemporaryFile(delete=False).name

def rangeFunction(begin, end, step):
    return list(range(begin, end, step))

def searchInText(regex: str, text: str):
    try:
        if re.findall(regex, text):
            return True
    except Exception as e:
        print(f" Error in 'BuiltSearchInText' -> {e}")
    return False

class _Functions(list):

    def __init__(self):
        super(_Functions, self).__init__()
        self.append({"name": "tmpFile", "native": True, "commands": tmpFileFunction})
        self.append({"name": "range", "native": True, "commands": rangeFunction})
        self.append({"name": "searchInText", "native": True, "commands": searchInText})

functions = _Functions()

__all__ = ("functions", )
