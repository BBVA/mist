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
import urllib.parse

from mist.lang.exceptions import (MistException, MistAbortException, MistUndefinedVariableException)
from mist.lang.config import config
from mist.lang.cmd import execution
import mist.lang.herlpers as helpers

from mist.lang.streams import streams

def tmpFileFunction(delete=False, stack:list=None, commands:list=None):
    """## tmpFile

Creates a temporary file and returns its path.

### Parameters
- delete - Boolean, defaults to false. The file is deleted after closing it.

### Return value
Returns the new temporary file's path.
    """
    return tempfile.NamedTemporaryFile(delete=delete).name

def fileWriteLine(name, line, stack:list=None, commands:list=None):
    """## writeLine

Writes a line of text in the given file.

### Parameters
- name - Path of the file to write to.
- line - String with the content of the line to write in the file.
    """
    with open(name, 't+a') as f:
        f.write(str(line) + '\n')

def rangeFunction(begin, end, step, stack:list=None, commands:list=None):
    """## range

Creates a list with values generated in the range defined by the parameters.

### Parameters
- begin - First value in the range.
- end - Last value, not included, in the range.
- step - Increment used to generate values, defaults to 1 if begin < end, -11 if end < begin.

### Return value
A list with all the values generated.
    """
    return list(range(begin, end, step))

def searchInText(regex: str, text: str, stack:list=None, commands:list=None):
    """## searchInText

Finds all the matches of the `regex` expresion in text.

### Parameters
- regex - Regular expression to define the search.
- text - The text to search in.

### Return value
A list with all the matches found.
    """
    found = []

    try:
        found = re.findall(regex, text)
    except Exception as e:
        print(f" Error in 'BuiltSearchInText' -> {e}")
    finally:
        return found

def searchInXML(xpath: str, text: str, stack:list=None, commands:list=None):
    """## searchInXML

Finds all the matches of the `xpath` expresion in a XML document.

### Parameters
- xpath - Xpath expression to define the search.
- text - The XML document to search in.

### Return value
A list with all the matches found.
    """
    found = None

    try:
        root = ET.fromstring(text)
        found = root.findall(xpath)
    except Exception as e:
        print(f" Error in 'BuiltSearchInXML' -> {e}")
    finally:
        return [ {"tag": e.tag, "text": e.text, "attributes": e.attrib } for e in found ] if found is not None else []

def searchInJSON(jsonpath: str, text: str, stack:list=None, commands:list=None):
    """## searchInJSON

Finds all the matches of the `JSONpath` expresion in a JSON document.

### Parameters
- jsonpath - JSONpath expression to define the search.
- text - The JSON document to search in.

### Return value
A list with all the matches found.
    """
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
    """## readJSON

Reads a JSON document from a file.

### Parameters
- jsonfilepath - Path to the file containing the JSON document.

### Return value
Returns a JSON document.
    """
    json_data = {}
    try:
        with open(jsonfilepath, 'r') as json_file:
            json_data = json.load(json_file)
    except Exception as e:
        return None
    return json_data

def parseJSON(jsonstr: str, stack:list=None, commands:list=None):
    """## parseJSON

Loads a JSON document from a string.

### Parameters
- jsonstr -  String containing the JSON document.

### Return value
Returns a JSON document.
    """
    json_data = None
    try:
        json_data = json.loads(jsonstr)
    except Exception as e:
        print(f" Error in 'parseJSON' -> {e}")
    finally:
        return json_data

def readFile(path:str, stack:list=None, commands:list=None):
    """## readFile

Reads the full content from a given file.

### Parameters
- path - File path.

### Return value
Returns the file content.
    """
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    with open(path, 'r') as f:
        fContent = f.read()

    return fContent

def readFileAsLines(path:str, stack:list=None, commands:list=None):
    """## readFileAsLines

Reads the full content from a given file as text lines.

### Parameters
- path - File path.

### Return value
Returns a list with all the lines readed from the file.
    """
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    fContent = []
    with open(path, 'r') as f:
        for l in f:
            fContent.append(l)

    return fContent

async def exec(command:str, printOutput=True, interactive=False, stack:list=None, commands:list=None):
    """## exec

Runs the given command and returns its output.

### Parameters
- command - Command line text to execute.
- printOutput - Print standard output to the MIST standard output, defaults to true.
- interactive - Runs the command in interactive mode, defaults to false.

### Return value
Returns a dictionary containing:
- result - True if the execution was succesfull
- resultCode - command exit code
- consoleOutput - commmand standard output
- consoleError - command standard error
    """
    with execution(command, interactive=interactive) as (executor, in_files, out_files):
        with executor as console_lines:
            async for output, process in console_lines:
                if isinstance(output, str):
                    if config.real_time and config.console_output and printOutput:
                        print(output)
                    if commands:
                        stack.append({"outputLine": output, "process": process})
                        await helpers.command_runner(commands, stack)
                        stack.pop()
            return {
                "result": executor.status_text(),
                "resultCode": executor.status(),
                "consoleOutput": executor.console_output(),
                "consoleError": executor.stderr_output()
            }

def objectLen(l, stack:list=None, commands:list=None):
    """## len

Returns the length of the given object.

### Parameters
- l - Object.

### Return value
Returns the length.
    """
    return len(l)

def listMap(l:list, mapFunc, stack:list=None, commands:list=None):
    """## map

Replace the elements of the given list by aplying the map function to each of them.

### Parameters
- l - List to process.
- mapFunc - The function to apply to the list elements, must be defined as mapFunc(val) => val.

### Return value
Returns the list modified.
    """
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
    """## reduce

Returns the value produced by reduceFunc after applyng it to all the elements of the given list.

### Parameters
- l - List to process.
- reduceFunc - The function to process the list elements, must be defined as reduceFunc(base, val) => val.

### Return value
Returns the value produced.
    """
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
    """## sleep

Sleep the current process during the given amount of time.

### Parameters
- seconds - Seconds to sleep, if given this value takes precedence.
- ms - Millieconds to sleep, if no secons parameter is given this value is used.
    """
    await asyncio.sleep(seconds if seconds else ms/1000)

def pythonEval(command:str, stack:list=None, commands:list=None):
    """## eval

Evaluates the given Python expressions.

### Parameters
- command - Python expression to evaluate.

### Return value
Retuens the result of evaluating the given expression.
    """
    return eval(command)

async def get(l, index, stack:list=None, commands:list=None):
    """## get

Return one element from a list or dictionary.

### Parameters
- l - List or Dictionary containing elements.
- index - The requested index (number for lists, string for dictionaries)

### Return value
Returns the element at the given index.
    """
    if "targetStream" in stack[-1]:
        await streams.send(stack[-1]["targetStream"][0], l[index])
    return l[index]

async def isEqual(left, right, stack:list=None, commands:list=None):
    """## isEqual

Compares two operands and execute the enclosed commands if both are equal.

### Parameters
- left - Operand to compare.
- right - Operand to compare.

### Return value
Returns true if both operands are equal, false otherwise.
    """
    if left == right and commands:
        await helpers.command_runner(commands, stack)
    return left == right

async def isGreater(left, right, stack:list=None, commands:list=None):
    """## isGreater

Compares two operands and execute the enclosed commands if `left` is greater than `right`.

### Parameters
- left - Operand to compare.
- right - Operand to compare.

### Return value
Returns true if `left` is greater than `right`, false otherwise.
    """
    if left > right and commands:
        await helpers.command_runner(commands, stack)
    return left > right

def contains(value, values, stack:list=None, commands:list=None):
    """## contains

Search `values` for `value` and returns true if it's contained.

### Parameters
- value - object to search for.
- values - Collection in which to look for.

### Return value
True if `values` contains `value`, false otherwise.
    """
    return value in values

async def ifCommand(val, stack:list=None, commands:list=None):
    """## if

Execute the enclosed commands if `val` is true.

### Parameters
- right - Boolean expression.

### Return value
Returns true if `val` is true, false otherwise.
    """
    if val and commands:
        await helpers.command_runner(commands, stack)
    return val

async def iterateCommand(items, name, stack:list=None, commands:list=None):
    """## iterate

Iterates over the elements of a collection while executing the enclosed commands.

### Parameters
- items - Collection.
- name - desc.
    """
    for item in items:
        stack[-1][name] = item
        await helpers.command_runner(commands, stack)
        del stack[-1][name]

def strSubstr(s, start=0, end=999999, step=1, stack:list=None, commands:list=None):
    """## strSubstr

Returns a substring.

### Parameters
- s - String.
- start - Start position.
- end - end position.

### Return value
Returns a substring.
    """
    return s[start:end:step]

def corePrint(*texts, stack:list=None, commands:list=None):
    """## print

Print the arguments in a standard output line.

### Parameters
- texts - Variable list of arguments to print.
    """
    print(*([json.dumps(t) if isinstance(t, dict) or isinstance(t, list) else t for t in texts if texts]))

def coreAbort(reason=None, stack:list=None, commands:list=None):
    """## abort

Abort mist script execution. The program will end inmediatelly and no registered finally hook will be executed.

### Parameters
- reason - A text describing the cause.
    """
    if not reason:
        reason = "Abort reached"

    raise MistAbortException(reason)

def parseInt(value, stack:list=None, commands:list=None):
    """## parseInt

Transforms the string value to integer if possible.

### Parameters
- value - String value.

### Return value
Integer representation of `value`.
    """
    return int(value)

def toString(value, stack:list=None, commands:list=None):
    """## toString

Converts the argument to string.

### Parameters
- value - The value to convert to string.

### Return value
`value` converted to string.
    """
    return str(value)

def boolNot(value, stack:list=None, commands:list=None):
    """## NOT

Boolean not operator.

### Parameters
- value

### Return value
Returns the negated value of `value`.
    """
    return (not bool(value))

def boolAnd(*values, stack:list=None, commands:list=None):
    """## AND

Boolean AND operator for the given values.

### Parameters
- values - List of values to apply the AND operation.

### Return value
Returns the resulting value of applying AND to all parameters.
    """
    ret = True

    for v in values:
        ret = ret and v

    return ret

def boolOr(*values, stack:list=None, commands:list=None):
    """## OR

Boolean OR operator for the given values.

### Parameters
- values - List of values to apply the OR operation.

### Return value
Returns the resulting value of applying OR to all parameters.
    """
    ret = False

    for v in values:
        ret = ret or v

    return ret

def terminate(stack:list=None, commands:list=None):
    """## terminate

Description.

### Parameters
- name - desc.
- name - desc.
    """
    helpers.get_var("process", stack).terminate()

def kill(stack:list=None, commands:list=None):
    """## kill

Kill the current process.
    """
    stack[-1]["process"].kill()

def processWriteLine(p, input, stack:list=None, commands:list=None):
    """## processWriteLine

Writes a line of text to a process standard input.

### Parameters
- p - Process descriptor.
- input - Text to write.
    """
    if not isinstance(input, str):
        input = json.dumps(input)
    p.stdin.writelines([bytes(input+"\n", 'utf-8')])

def uuidStr(stack:list=None, commands:list=None):
    """## uuidStr

Generates and returns a UUID version 4.

### Return value
The generated UUID.
"""
    return str(uuid.uuid4())

async def filterDict(d:dict, names:list, newNames:list=None, stack:list=None, commands:list=None):
    """## filterDict

Returns a dictionary containing only the selected entries. If `newNames` is provided the keys are replaced.

### Parameters
- d - Source dictionary.
- names - List of keys to filter.
- newNames - Replacement values for the filtered keys

### Return and send value
The filtered dictionary.
    """
    result = {}
    for index, name in enumerate(names):
        if newNames:
            result[newNames[index]] = d[name]
        else:
            result[name] = d[name]
    if "targetStream" in stack[-1]:
        await streams.send(stack[-1]["targetStream"][0], result)
    return result
    
async def list2dict(l:list, names:list, stack:list=None, commands:list=None):
    """## list2dict

Convert a list into a dictionary.

### Parameters
- l - source list.
- names - list of names for the resulting dictionary.

### Return and sent value
The resulting dictionary.
    """
    result = {}
    for index, value in enumerate(l):
        result[names[index]] = value
    if "targetStream" in stack[-1]: 
        await streams.send(stack[-1]["targetStream"][0], result)
    return result

async def dict2list(d:dict, names:list, stack:list=None, commands:list=None):
    """## dict2list

Convert a dictionary into a list.

### Parameters
- l - source dictionary.
- names - list of key to include into the resulting list.

### Return and sent value
The resulting list.
    """
    result = []
    for value in names:
        result.append(d[value])
    if "targetStream" in stack[-1]: 
        await streams.send(stack[-1]["targetStream"][0], result)
    return result

finallyHooks = []
def registerFinallyHook(fname, *p, stack:list=None, commands:list=None):
    """## registerFinallyHook

Register a function to be executed at the end of the program

### Parameters
- fname - string with the name of the function
- *p - parameters for the function
    """
    finallyHooks.append((fname, [*p], stack, commands))

def urlEncode(s, stack:list=None, commands:list=None):
    """## urlEncode

Encode an string as url

### Parameters
- s - string to encopde

### Return and sent value
The resulting encoded string
    """
    return urllib.parse.quote(s)

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
        self["readFile"] = {"native": True, "commands": readFile}
        self["readFileAsLines"] = {"native": True, "commands": readFileAsLines}
        self["exec"] = {"native": True, "commands": exec, "async": True}
        self["len"] = {"native": True, "commands": objectLen}
        self["map"] = {"native": True, "commands": listMap}
        self["reduce"] = {"native": True, "commands": listReduce}
        self["sleep"] = {"native": True, "commands": sleep, "async": True}
        self["eval"] = {"native": True, "commands": pythonEval}
        self["get"] = {"native": True, "commands": get, "async": True}
        self["isEqual"] = {"native": True, "commands": isEqual, "async": True}
        self["isGreater"] = {"native": True, "commands": isGreater, "async": True}
        self["contains"] = {"native": True, "commands": contains}
        self["if"] = {"native": True, "commands": ifCommand, "async": True}
        self["iterate"] = {"native": True, "commands": iterateCommand, "async": True}
        self["strSubstr"] = {"native": True, "commands": strSubstr}
        self["print"] = {"native": True, "commands": corePrint}
        self["abort"] = {"native": True, "commands": coreAbort}
        self["parseInt"] = {"native": True, "commands": parseInt}
        self["toString"] = {"native": True, "commands": toString}
        self["NOT"] = {"native": True, "commands": boolNot}
        self["AND"] = {"native": True, "commands": boolAnd}
        self["OR"] = {"native": True, "commands": boolOr}
        self["terminate"] = {"native": True, "commands": terminate}
        self["kill"] = {"native": True, "commands": kill}
        self["processWriteLine"] = {"native": True, "commands": processWriteLine}
        self["uuidStr"] = {"native": True, "commands": uuidStr}
        self["filterDict"] = {"native": True, "commands": filterDict, "async": True}
        self["list2dict"] = {"native": True, "commands": list2dict, "async": True}
        self["dict2list"] = {"native": True, "commands": dict2list, "async": True}
        self["registerFinallyHook"] = {"native": True, "commands": registerFinallyHook}
        self["urlEncode"] = {"native": True, "commands": urlEncode}

functions = _Functions()

__all__ = ("functions", "finallyHooks")
