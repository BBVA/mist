import re
from typing import List
from string import Formatter

from mist.sdk.db import db
from mist.sdk.config import config
from mist.sdk.watchers import watchers
from mist.sdk.environment import environment
from mist.sdk.params import params
from mist.sdk.function import functions

from mist.lang.streams import streams

def get_var(var, stack):
    #print(f"get_var {var}", file=sys.stderr, flush=True)
    if var in ("True", "Success"):
        return True
    if var in ("False", "Error"):
        return False
    try:
        return int(var)
    except ValueError:
        pass
    for s in reversed(stack):
        if var in s:
            return s[var]
    return db.fetch_table_as_dict(var)

def getFromDict(d, childs):
    return d[childs[0]] if len(childs) == 1 else getFromDict(d[childs[0]], childs[1:])

def getChildFromVar(t, childs):
    if type(t) is list:
        return getFromDict(t[0], childs)
    else:
        return getFromDict(t, childs)

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

async def function_runner(name, stack, sourceStream, targetStream, args, namedArgs=None):
    namedArgsDict = {}
    if args:
        args = [await checkArg(a, stack) for a in args]
    elif namedArgs:
        for i in namedArgs:
            namedArgsDict[i.key] = await checkArg(i.value, stack)
    f = functions[name]
    if "native" in f and f["native"]:
        #TODO: handle targetStream and sourceStream if needed
        if "async" in f and f["async"]:
            if args:
                return await f["commands"](*args, stack=stack)
            elif namedArgs:
                namedArgsDict["stack"]=stack
                return await f["commands"](**namedArgsDict)
            else:
                return await f["commands"](stack=stack)
        else:
            if args:
                return f["commands"](*args, stack=stack)
            elif namedArgs:
                namedArgsDict["stack"]=stack
                return f["commands"](**namedArgsDict)
            else:
                return f["commands"](stack=stack)
    else:
        if args:
            namedArgsDict = dict(zip(f["args"], args))
        namedArgsDict["MistBaseNamespace"] = True
        if targetStream:
            namedArgsDict["targetStream"] = targetStream
        stack.append(namedArgsDict)
        if sourceStream:
            queue, position, namedName = findQueueInArgs(args, namedArgsDict)
            namePlaceHolder = next(key for key, value in namedArgsDict.items() if value == ":" + queue)
            async for s in streams[queue].iterate():
                namedArgsDict[namePlaceHolder] = s
                await command_runner(f["commands"], stack)
        else:
            await command_runner(f["commands"], stack)
        lastStack = stack.pop()
        return lastStack[f["result"]] if f["result"]!='' and f["result"] in lastStack else None

async def get_id(id, stack):
    #print(f'get_id id={id.id} hasAttrString={hasattr(id, "string")} string={id.string} function={id.function} childs={id.childs} var={id.var} param={id.param} intVal={id.intVal}', file=sys.stderr, flush=True)
    if id == None:
        return None
    if isinstance(id, int):
        return id
    if not hasattr(id, "string"):
        return get_var(id, stack)
    if id.function:
       return await function_runner(id.function.name, stack, None, None, id.function.args, id.function.namedArgs )
    if id.customList:
        return [
            await get_id(c, stack)
            for c in id.customList.components
        ]
    if id.var:
        return environment[id.var]
    if id.param:
        return params[id.param]
    if id.source:
        return ":" + id.source
    if id.string:
        s=id.string
        pairs = [(i[1],await get_key(i[1], stack)) for i in Formatter().parse(s) if i[1] is not None]
        for k,v in pairs:
            s = s.replace('{' + k + '}',str(v),1)
        return s
    elif id.data:
        return id.data
    elif id.childs:
        return getChildFromVar(get_var(id.id, stack), id.childs)
    if id.id == "":
        return id.intVal
    else:
        return get_var(id.id, stack)

def get_param(params, key):
    t = [x for x in params if x.key == key]
    return t[0].value if t else None

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
    if key[-1]==')':
        function = key.split('(')[0].strip()
        args = re.sub(' +', ' ', key.split('(',1)[1]).rsplit(')',1)[0].strip().split(',')
        if '=' in args[0]:
            class NamedArg:
                def __init__(self, key, value):
                    self.key = key
                    self.value = value
            namedArgs=[ NamedArg(i.split('=',1)[0].strip(), i.split('=',1)[1].strip()) for i in args]
            return await function_runner(function, stack, None, None, None, namedArgs )
        return await function_runner(function, stack, None, None, [] if args[0]=='' else args)
    if '.' in key:
        t = key.split('.')
        return getChildFromVar(get_var(t[0], stack), t[1:])
    return get_var(key, stack)

async def command_runner(commands: list, stack):
    for c in commands:
        if c == "done":
            break
        await c.launch(stack)
