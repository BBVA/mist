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

class _Functions(dict):

    def __init__(self):
        super(_Functions, self).__init__()
        self["tmpFile"] = {"native": True, "commands": tmpFileFunction}
        self["range"] = {"native": True, "commands": rangeFunction}
        self["searchInText"] = {"native": True, "commands": searchInText}

functions = _Functions()

__all__ = ("functions", )
