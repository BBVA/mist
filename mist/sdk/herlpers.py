from typing import List

from mist.sdk.stack import stack
from mist.sdk.db import db
from mist.sdk.config import config
from mist.sdk.watchers import watchers
from mist.sdk.environment import environment
from mist.sdk.params import params
from mist.sdk.functions import functions

def get_var(var):
    #print(f"get_var {var}")
    if var in ("True", "Success"):
        return True
    elif var in ("False", "Error"):
        return False
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

def function_runner(name, args):
    for f in functions:
        if f["name"] == name :
            if "native" in f and f["native"]:
                return f["commands"](*args)
            else:
                print("TODO")

def get_id(id):
    # print(f"get_id id={id.id} string={id.string} childs={id.childs} var={id.var} param={id.param}")
    if id == None:
        return None
    if not hasattr(id, "string"):
        return get_var(id)
    if id.function:
       return function_runner(id.function.name, [get_id(a) for a in id.function.args])
    if id.customList:
        return [
            get_id(c)
            for c in id.customList.components
        ]
    if id.var:
        return environment[id.var]
    if id.param:
        return params[id.param]
    if id.string:
        return id.string
    elif id.data:
        return id.data
    elif id.childs:
        return getChildFromVar(get_var(id.id), id.childs)
    return get_var(id.id)

def watchedInsert(table: str, values: List[str], *, fields=None):
    if config.debug:
        print(f"-> watchedInsert {table}")
    db.insert(table, values, fields=fields)
    if not fields:
        fields=db.fetch_table_headers(table)[1:]
    item = dict(zip(fields, values))

    for watcher in watchers:
        if watcher["var"] == table:
            stack.append({watcher["name"]: item})
            for c in watcher["commands"]:
                c.launch()
            stack.pop()

def get_param(params, key):
    t = [x for x in params if x.key == key]
    return t[0].value if t else None

def get_key(key):
    if key[0]=="'" and key[-1]=="'":
        return key[1:-1]
    if key[0]=='%':
        return params[key[1:]]
    if key[0]=='$':
        return environment[key[1:]]
    if key[-1]==')':
        t = key.split('(')
        return function_runner(t[0], [get_key(a) for a in t[1][:-1].split(' ')] if len(t[1])>1 else [])
    elif '.' in key:
        t = key.split('.')
        return getChildFromVar(get_var(t[0]), t[1:])
    return get_var(key)

def command_runner(commands: list):
    for c in commands:
        if c == "done":
            break
        c.launch()
