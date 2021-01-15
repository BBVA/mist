import os
import tempfile
import re
import xml.etree.ElementTree as ET
import json
from jsonpath_ng.ext import parse
import csv
import asyncio

from mist.sdk import db
from mist.sdk.exceptions import MistException
from mist.sdk.config import config
from mist.sdk.common import watchedInsert
from mist.sdk.cmd import execution

def tmpFileFunction(stack: list = None):
    return tempfile.NamedTemporaryFile(delete=False).name

def rangeFunction(begin, end, step, stack: list = None):
    return list(range(begin, end, step))

def searchInText(regex: str, text: str, stack: list = None):
    found = []

    try:
        found = re.findall(regex, text)
    except Exception as e:
        print(f" Error in 'BuiltSearchInText' -> {e}")
    finally:
        return found

def searchInXML(xpath: str, text: str, stack: list = None):
    found = None

    try:
        root = ET.fromstring(text)
        found = root.findall(xpath)
    except Exception as e:
        print(f" Error in 'BuiltSearchInXML' -> {e}")
    finally:
        return [ {"tag": e.tag, "text": e.text, "attributes": e.attrib } for e in found ] if found is not None else []

def searchInJSON(jsonpath: str, text: str, stack: list = None):
    found = None

    try:
        json_data = json.loads(text)
        jsonpath_expression = parse(jsonpath)
        found = jsonpath_expression.find(json_data)
    except Exception as e:
        print(f" Error in 'BuiltSearchInJSON' -> {e}")
    finally:
        return [ e.value for e in found ] if found is not None else []


async def CSVput(fileName: str, target: str, stack: list = None):
    with open(fileName) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        try:
            # TODO: ADD CSV HEADER?
            headers = next(reader)

            db.create_table(target, headers)
            for row in reader:
                await watchedInsert(target, stack, row)
            return True
        except StopIteration:
            raise MistException(f"Empty file: {fileName}")
            return False
        except Exception as e:
            print(f"Error while creating database: {target}: {e}")
            return False

def CSVdump(source: str, fileName: str, stack: list = None):
    with open(fileName, mode='w') as csvFile:
        csvWriter = csv.writer(csvFile,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        headers = db.fetch_table_headers(source)[1:]
        csvWriter.writerow(headers)
        items = db.fetch_table_as_dict(source)
        for row in items:
            row.pop('id', None)
        csvWriter.writerows([
            row.values()
            for row in items
        ])

def readFile(path:str, stack: list = None):
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    with open(path, 'r') as f:
        fContent = f.read()

    return fContent

def readFileAsLines(path:str, stack: list = None):
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    fContent = []
    with open(path, 'r') as f:
        for l in f:
            fContent.append(l)

    return fContent

def exec(command:str, printOutput=True, stack: list = None):
    with execution(command) as (executor, in_files, out_files):
        with executor as console_lines:
            for line in console_lines:
                if config.real_time and config.console_output and printOutput:
                    print(line)
        return {
            "result": executor.status_text(),
            "resultCode": executor.status(),
            "consoleOutput": executor.console_output(),
            "consoleError": executor.stderr_output()
        }

def listLen(l:list, stack: list = None):
    """ Returns the length of the given list """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")

    return len(l)

def listClear(l:list, stack: list = None):
    """ Removes all elements from the given list """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")

    l.clear()
    return l

def listSort(l:list, stack: list = None):
    """ Sorts the given list in ascending order """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")

    l.sort()
    return l

def listReverse(l:list, stack: list = None):
    """ Reverses the elements of the given list """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")

    l.reverse()
    return l

def listAppend(l:list, *elements, stack: list = None):
    """ Appends all the elements to the given list """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")
    if len(elements) == 0:
        raise MistException("No elements received")

    for e in elements:
        l.append(e)

    return l

def listRemove(l:list, e, stack: list = None):
    """ Removes the element from the given list if it exists """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")

    try:
        l.remove(e)
    except ValueError:
        pass

    return l

def listMap(l:list, mapFunc, stack: list = None):
    """ Replace the elements of the given list by aplying the map function to each of them. mapFunc must be defined as mapFunc(val) => val """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")
    if not callable(mapFunc):
        raise MistException("Not a function")

    for i, val in enumerate(l):
        l[i] = mapFunc(val)

    return l

def listReduce(l:list, reduceFunc, stack: list = None):
    """ Returns the value produced by reduceFunc after applyng it to all the elements of the given list. reduceFunc must be defined as reduceFunc(base, val) => val """
    if l is None:
        raise MistException("No list received")
    if not isinstance(l, list):
        raise MistException("Not a list")
    if not callable(reduceFunc):
        raise MistException("Not a function")

    base = None
    for val in l:
        base = reduceFunc(base, val)

    return base

async def sleep(n:int, stack: list = None):
    await asyncio.sleep(n)

class _Functions(dict):

    def __init__(self):
        super(_Functions, self).__init__()
        self["tmpFile"] = {"native": True, "commands": tmpFileFunction}
        self["range"] = {"native": True, "commands": rangeFunction}
        self["searchInText"] = {"native": True, "commands": searchInText}
        self["searchInXML"] = {"native": True, "commands": searchInXML}
        self["searchInJSON"] = {"native": True, "commands": searchInJSON}
        self["CSVput"] = {"native": True, "commands": CSVput, "async": True}
        self["CSVdump"] = {"native": True, "commands": CSVdump}
        self["readFile"] = {"native": True, "commands": readFile}
        self["readFileAsLines"] = {"native": True, "commands": readFileAsLines}
        self["exec"] = {"native": True, "commands": exec}
        self["len"] = {"native": True, "commands": listLen}
        self["clear"] = {"native": True, "commands": listClear}
        self["sort"] = {"native": True, "commands": listSort}
        self["reverse"] = {"native": True, "commands": listReverse}
        self["append"] = {"native": True, "commands": listAppend}
        self["remove"] = {"native": True, "commands": listRemove}
        self["map"] = {"native": True, "commands": listMap}
        self["reduce"] = {"native": True, "commands": listReduce}
        self["sleep"] = {"native": True, "commands": sleep, "async": True}

functions = _Functions()

__all__ = ("functions", )
