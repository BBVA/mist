import re
from typing import List
from string import Formatter
#import inspect
import asyncio

from mist.lang.config import config
from mist.lang.environment import environment
from mist.lang.params import params
from mist.lang.streams import streams
from mist.lang.exceptions import MistUndefinedVariableException

def get_var(var, stack):
    #print(f"get_var {var}", file=sys.stderr, flush=True)
    if var in ("True", "Success"):
        return True
    if var in ("False", "Error"):
        return False
    if var in ("None", "Null"):
        return None
    try:
        return int(var)
    except ValueError:
        pass
    for s in reversed(stack):
        if var in s:
            return s[var]
    raise MistUndefinedVariableException(var)

def getChildFromVar(t, childs):
    if type(t) is dict and childs[0] in t:
        v = t[childs[0]]
    else:    
        v = getattr(t, childs[0])
    return v if len(childs) == 1 else getChildFromVar(v, childs[1:])


async def checkArg(v, stack):
    if isinstance(v, str):
        return await get_key(v, stack)
    else:
        return await get_id(v, stack)

def findQueueInArgs(args, namedArgsDict):
    if args:
        for i, arg in enumerate(args):
            if isinstance(arg, str) and arg[0] == ":":
                #return {"position": i, "name": None, "queue": arg.source }
                return arg[1:], i, None
    elif namedArgsDict:
        for key, value in namedArgsDict.items():
            if isinstance(value, str) and value[0] == ":":
                return value[1:], None, key
    #TODO: raise queue not found exception
    return None, None, None

async def callNative(f, args, namedArgs, namedArgsDict, stack, commands):
    if "async" in f and f["async"]:
    #if inspect.iscoroutinefunction(f["commands"]):
        if hasattr(f["commands"], "__annotations__") and "stack" in getattr(f["commands"], "__annotations__"):
            if args:
                return await f["commands"](*args, stack=stack, commands=commands)
            elif namedArgs:
                namedArgsDict["stack"]=stack
                namedArgsDict["commands"]=commands
                return await f["commands"](**namedArgsDict)
            else:
                return await f["commands"](stack=stack, commands=commands)
        else:
            if args:
                return await f["commands"](*args)
            elif namedArgs:
                return await f["commands"](**namedArgsDict)
            else:
                return await f["commands"]()
    else:
        if hasattr(f["commands"], "__annotations__") and "stack" in getattr(f["commands"], "__annotations__"):
            if args:
                return f["commands"](*args, stack=stack, commands=commands)
            elif namedArgs:
                namedArgsDict["stack"]=stack
                namedArgsDict["commands"]=commands
                return f["commands"](**namedArgsDict)
            else:
                return f["commands"](stack=stack, commands=commands)
        else:
            if args:
                return f["commands"](*args)
            elif namedArgs:
                return f["commands"](**namedArgsDict)
            else:
                return f["commands"]()

async def function_runner(name, stack, sourceStream, targetStream, args, namedArgs=None, commands=None, processArgs=True):
    namedArgsDict = {}
    if processArgs:
        if args:
            args = [await checkArg(a, stack) for a in args]
        elif namedArgs:
            for i in namedArgs:
                namedArgsDict[i.key] = await checkArg(i.value, stack)
    if name.childs:
        o = await name.getValue(stack)
        f = {"native": True, "commands": o}
    else:
        from mist.lang.function import functions as functions
        f = functions[name.id]
    isNative = "native" in f and f["native"]
    if not isNative and args:
        namedArgsDict = dict(zip(f["args"], args))
    if targetStream:
        namedArgsDict["targetStream"] = targetStream
    stack.append(namedArgsDict)
    if sourceStream:
        queue, position, namedName = findQueueInArgs(args, namedArgsDict)
        if not isNative:
            namePlaceHolder = next(key for key, value in namedArgsDict.items() if value == ":" + queue)
        async for s in streams[queue].iterate():
            if isNative:
                args[position] = s
                await callNative(f, args, namedArgs, namedArgsDict, stack, commands)
            else:
                namedArgsDict[namePlaceHolder] = s
                if "MistFunctionResultTmpVariable" in stack[-1]:
                    del stack[-1]["MistFunctionResultTmpVariable"]
                await command_runner(f["commands"], stack)
    else:
        if isNative:
            if targetStream:
                stack[-1]["targetStream"] = targetStream
            result = await callNative(f, args, namedArgs, namedArgsDict, stack, commands)
            stack.pop()
            return result
        await command_runner(f["commands"], stack)
        lastStack = stack.pop()
        return lastStack["MistFunctionResultTmpVariable"] if "MistFunctionResultTmpVariable" in lastStack else None

# Define interface for ValueContainer with a getValue() method for classes that
# hold a left-side value
# And a MistCallable for classes that represent function executions with
# method launch to be invoked
class ValueContainer:
    async def getValue(self, stack):
        pass

class MistCallable:
    async def launch(self, stack):
        pass

async def get_id(id, stack):

    if id == None:
        return None

    if isinstance(id, str):
        return get_var(id, stack)
    elif isinstance(id.value, MistCallable):
        result = await id.value.launch(stack)
        return result
    elif isinstance(id.value, str):
        s = id.value
        pairs = [(i[1],await get_key(i[1], stack)) for i in Formatter().parse(s) if i[1] is not None]
        for k,v in pairs:
            s = s.replace('{' + k + '}',str(v),1)
        return s
    elif isinstance(id.value, int):
        return id.value
    elif isinstance(id.value, ValueContainer):
        return await id.value.getValue(stack)
    else: # type(id.value is boolean, float, ....)
        pass


def get_param(params, key):
    t = [x for x in params if x.key == key]
    return t[0].value if t else None

class NamedArg:
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __eq__(self, other):
        return isinstance(other, NamedArg) and self.key == other.key and self.value == other.value

LDREF_MATCHER = re.compile(r"(\w*)\[(.*)\]")

async def get_key(key, stack):
    key=key.strip()
    if key[0]=="'" and key[-1]=="'":
        return key[1:-1]
    if key[0]=='%':
        return params[key[1:]]
    if key[0]=='$':
        return environment[key[1:]]
    if key[0]==':':
        return key
    if key[-1]==']': # List or dictionary reference
        if grs := LDREF_MATCHER.fullmatch(key):
            return await resolve_list_dict_reference(grs.group(1), grs.group(2), stack)
        else:
            raise MistException(f"Invalid reference {key}")
    if key[-1]==')':
        function = key.split('(')[0].strip().split(".")
        from mist.lang.classes import VarReference
        method = VarReference(None, function[0], function[1:])
        args = [i.strip() for i in re.sub(' +', ' ', key.split('(',1)[1]).rsplit(')',1)[0].strip().split(',')]
        if '=' in args[0]:
            namedArgs=[ NamedArg(i.split('=',1)[0].strip(), i.split('=',1)[1].strip()) for i in args]
            return await function_runner(method, stack, None, None, None, namedArgs )
        return await function_runner(method, stack, None, None, [] if args[0]=='' else args)
    if '.' in key:
        t = key.split('.')
        return getChildFromVar(get_var(t[0], stack), t[1:])
    return get_var(key, stack)

async def resolve_list_dict_reference(id, member, stack):
    i = get_var(id, stack)
    if i is None:
        raise MistUndefinedVariableException(id)
    if isinstance(member, int):
        m = member
    elif isinstance(member, str) and (member[0] == "'" and member[-1] == "'" or member[0] == '"' and member[-1] == '"'):
        m = member[1:-1]
    else:
        m = await get_id(member, stack)
    if isinstance(i, list):
        try:
            return i[m]
        except IndexError:
            return None
    elif isinstance(i, dict):
        return i.get(m, None)
    else:
        raise TypeError(f"{id} is not a list neither a dict")

async def command_runner(commands: list, stack):
    for c in commands:
        if len(stack)>1:                            # We're running inside a function
            if "MistFunctionResultTmpVariable" in stack[-1]:               # The function returns, we stop executing it commands
                return

        if c == "done":
            break
        await c.launch(stack)
