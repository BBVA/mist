import os
import tempfile
import re
import xml.etree.ElementTree as ET
import json
from jsonpath_ng.ext import parse
import csv
import asyncio
import inspect
from functools import partial
import uuid

from mist.sdk import db
from mist.sdk.exceptions import (MistException, MistAbortException, MistUndefinedVariableException)
from mist.sdk.config import config
from mist.sdk.common import watchedInsert
from mist.sdk.cmd import execution
import mist.sdk.herlpers as helpers

from mist.lang.streams import streams

def tmpFileFunction(delete=False, stack:list=None, commands:list=None):
    return tempfile.NamedTemporaryFile(delete=delete).name

def fileWriteLine(name, line, stack:list=None, commands:list=None):
    with open(name, 't+a') as f:
        f.write(str(line) + '\n')

def rangeFunction(begin, end, step, stack:list=None, commands:list=None):
    return list(range(begin, end, step))

def searchInText(regex: str, text: str, stack:list=None, commands:list=None):
    found = []

    try:
        found = re.findall(regex, text)
    except Exception as e:
        print(f" Error in 'BuiltSearchInText' -> {e}")
    finally:
        return found

def searchInXML(xpath: str, text: str, stack:list=None, commands:list=None):
    found = None

    try:
        root = ET.fromstring(text)
        found = root.findall(xpath)
    except Exception as e:
        print(f" Error in 'BuiltSearchInXML' -> {e}")
    finally:
        return [ {"tag": e.tag, "text": e.text, "attributes": e.attrib } for e in found ] if found is not None else []

def searchInJSON(jsonpath: str, text: str, stack:list=None, commands:list=None):
    found = None

    try:
        json_data = json.loads(text)
        jsonpath_expression = parse(jsonpath)
        found = jsonpath_expression.find(json_data)
    except Exception as e:
        print(f" Error in 'BuiltSearchInJSON' -> {e}")
    finally:
        return [ e.value for e in found ] if found is not None else []

def readJSON(jsonfilepath: str, stack:list=None, commands:list=None):
    json_data = {}
    try:
        with open(jsonfilepath, 'r') as json_file:
            json_data = json.load(json_file)
    except Exception as e:
        return None
    return json_data

def parseJSON(jsonstr: str, stack:list=None, commands:list=None):
    json_data = None
    try:
        json_data = json.loads(jsonstr)
    except Exception as e:
        print(f" Error in 'parseJSON' -> {e}")
    finally:
        return json_data

async def CSVput(fileName: str, target: str, stack:list=None, commands:list=None):
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

def CSVdump(source: str, fileName: str, stack:list=None, commands:list=None):
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

def readFile(path:str, stack:list=None, commands:list=None):
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    with open(path, 'r') as f:
        fContent = f.read()

    return fContent

def readFileAsLines(path:str, stack:list=None, commands:list=None):
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    fContent = []
    with open(path, 'r') as f:
        for l in f:
            fContent.append(l)

    return fContent

async def exec(command:str, printOutput=True, interactive=False, stack:list=None, commands:list=None):
    with execution(command, interactive=interactive) as (executor, in_files, out_files):
        with executor as console_lines:
            async for output, process in console_lines:
                if isinstance(output, str):
                    if config.real_time and config.console_output and printOutput:
                        print(output)
                    if commands:
                        stack.append({"outputLine": output})
                        stack.append({"process": process})
                        await helpers.command_runner(commands, stack)
                        stack.pop()
            return {
                "result": executor.status_text(),
                "resultCode": executor.status(),
                "consoleOutput": executor.console_output(),
                "consoleError": executor.stderr_output()
            }

def objectLen(l, stack:list=None, commands:list=None):
    """ Returns the length of the given object """
    return len(l)

def listMap(l:list, mapFunc, stack:list=None, commands:list=None):
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

def listReduce(l:list, reduceFunc, stack:list=None, commands:list=None):
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

async def sleep(seconds:int=None, ms:int=0, stack:list=None, commands:list=None):
    await asyncio.sleep(seconds if seconds else ms/1000)

def pythonEval(command:str, stack:list=None, commands:list=None):
    return eval(command)

def autoCall(f, *args, stack:list=None, commands:list=None):
    result = f(*args)
    return result if result else args[0]

def get(l, index, stack:list=None, commands:list=None):
    return l[index]

async def isEqual(left, right, stack:list=None, commands:list=None):
    if left == right and commands:
        await helpers.command_runner(commands, stack)
    return left == right

async def isGreater(left, right, stack:list=None, commands:list=None):
    if left > right and commands:
        await helpers.command_runner(commands, stack)
    return left > right

def contains(value, values, stack:list=None, commands:list=None):
    return value in values

async def ifCommand(val, stack:list=None, commands:list=None):
    if val and commands:
        await helpers.command_runner(commands, stack)
    return val

async def iterateCommand(items, name, stack:list=None, commands:list=None):
    for item in items:
        stack[-1][name] = item
        await helpers.command_runner(commands, stack)
        del stack[-1][name]

def strSubstr(s, start=0, end=999999, step=1, stack:list=None, commands:list=None):
    return s[start:end:step]

def corePrint(*texts, stack:list=None, commands:list=None):

    print(*([t for t in texts if texts]))

def coreAbort(reason=None, stack:list=None, commands:list=None):

    if not reason:
        reason = "Abort reached"

    raise MistAbortException(reason)

async def corePut(table, *args, stack:list=None, commands:list=None):
    if not table:
        raise MistException("A table is needed")
    if not args:
        raise MistException("Data items to store needed")

    data = [ json.dumps(d) if type(d) is list else str(d) for d in args ]

    await watchedInsert(table, stack, data, fields=None)

async def corePutData(table, data, stack:list=None, commands:list=None):
    if not table:
        raise MistException("A table is needed")
    if not data:
        raise MistException("Data items to store needed")
    if not isinstance(data, dict):
        raise TypeError("Data must come in a dictionary")

    values = []
    fields = []
    for k, v in data.items():
        values.append(json.dumps(v) if type(v) is list else str(v))
        fields.append(k)

    await watchedInsert(table, stack, values, fields)

async def coreSend(value, targetStream=None, stack:list=None, commands:list=None):
    if value is not None :
        if not targetStream:
            try:
                targetStream = await helpers.get_key("targetStream", stack)
            except MistUndefinedVariableException as e:
                return

        await streams.send(targetStream, value)

def parseInt(value, stack:list=None, commands:list=None):
    return int(value)

def toString(value, stack:list=None, commands:list=None):
    return str(value)

def boolNot(value, stack:list=None, commands:list=None):
    return (not bool(value))

def boolAnd(*values, stack:list=None, commands:list=None):
    ret = True

    for v in values:
        ret = ret and v

    return ret

def boolOr(*values, stack:list=None, commands:list=None):
    ret = False

    for v in values:
        ret = ret or v

    return ret

def terminate(stack:list=None, commands:list=None):
    stack[-1]["process"].terminate()

def kill(stack:list=None, commands:list=None):
    stack[-1]["process"].kill()

def processWriteLine(p, input, stack:list=None, commands:list=None):
    if not isinstance(input, str):
        input = json.dumps(input)
    p.stdin.writelines([bytes(input+"\n", 'utf-8')])

def uuidStr(stack:list=None, commands:list=None):
    return str(uuid.uuid4())

class _Functions(dict):

    def __init__(self):
        super(_Functions, self).__init__()
        self["tmpFile"] = {"native": True, "commands": tmpFileFunction}
        self["writeLine"] = {"native": True, "commands": fileWriteLine}
        self["range"] = {"native": True, "commands": rangeFunction}
        self["searchInText"] = {"native": True, "commands": searchInText}
        self["searchInXML"] = {"native": True, "commands": searchInXML}
        self["searchInJSON"] = {"native": True, "commands": searchInJSON}
        self["readJSON"] = {"native": True, "commands": readJSON}
        self["parseJSON"] = {"native": True, "commands": parseJSON}
        self["CSVput"] = {"native": True, "commands": CSVput, "async": True}
        self["CSVdump"] = {"native": True, "commands": CSVdump}
        self["readFile"] = {"native": True, "commands": readFile}
        self["readFileAsLines"] = {"native": True, "commands": readFileAsLines}
        self["exec"] = {"native": True, "commands": exec, "async": True}
        self["len"] = {"native": True, "commands": objectLen}
        self["map"] = {"native": True, "commands": listMap}
        self["reduce"] = {"native": True, "commands": listReduce}
        self["sleep"] = {"native": True, "commands": sleep, "async": True}
        self["eval"] = {"native": True, "commands": pythonEval}
        self["get"] = {"native": True, "commands": get}
        self["isEqual"] = {"native": True, "commands": isEqual, "async": True}
        self["isGreater"] = {"native": True, "commands": isGreater, "async": True}
        self["contains"] = {"native": True, "commands": contains}
        self["if"] = {"native": True, "commands": ifCommand, "async": True}
        self["iterate"] = {"native": True, "commands": iterateCommand, "async": True}
        self["strSubstr"] = {"native": True, "commands": strSubstr}
        self["print"] = {"native": True, "commands": corePrint}
        self["abort"] = {"native": True, "commands": coreAbort}
        self["put"] = {"native": True, "commands": corePut, "async": True}
        self["putData"] = {"native": True, "commands": corePutData, "async": True}
        self["send"] = {"native": True, "commands": coreSend, "async": True}
        self["parseInt"] = {"native": True, "commands": parseInt}
        self["toString"] = {"native": True, "commands": toString}
        self["NOT"] = {"native": True, "commands": boolNot}
        self["AND"] = {"native": True, "commands": boolAnd}
        self["OR"] = {"native": True, "commands": boolOr}
        self["terminate"] = {"native": True, "commands": terminate}
        self["kill"] = {"native": True, "commands": kill}
        self["processWriteLine"] = {"native": True, "commands": processWriteLine}
        self["uuidStr"] = {"native": True, "commands": uuidStr}

        # Incorporate all functions of str, dict and list classes:
        # strCapitalize, strCasefold, strCenter, strCount, strEncode, strEndswith, strExpandtabs, strFind, strFormat, strFormat_map, strIndex, strIsalnum, strIsalpha, strIsascii, strIsdecimal, strIsdigit, strIsidentifier, strIslower, strIsnumeric, strIsprintable, strIsspace, strIstitle, strIsupper, strJoin, strLjust, strLower, strLstrip, strMaketrans, strPartition, strReplace, strRfind, strRindex, strRjust, strRpartition, strRsplit, strRstrip, strSplit, strSplitlines, strStartswith, strStrip, strSwapcase, strTitle, strTranslate, strUpper, strZfill, dictClear, dictCopy, dictFromkeys, dictGet, dictItems, dictKeys, dictPop, dictPopitem, dictSetdefault, dictUpdate, dictValues, listAppend, listClear, listCopy, listCount, listExtend, listIndex, listInsert, listPop, listRemove, listReverse, listSort
        for c in [str, dict, list]:
            for f in inspect.getmembers(c):
                if f[0][0] != "_" and callable(f[1]):
                    name = c.__name__ + f[0][0].upper() + f[0][1:]
                    self[name] = {"native": True, "commands": partial(autoCall,f[1])}

functions = _Functions()

__all__ = ("functions", )
