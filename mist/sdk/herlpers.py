from typing import List

from mist.sdk.stack import stack
from mist.sdk.db import db
from mist.sdk.config import config
from mist.sdk.watchers import watchers
from mist.sdk.environment import environment
from mist.sdk.params import params

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

def get_id(id):
    # print(f"get_id id={id.id} string={id.string} child={id.child} var={id.var} param={id.param}")
    if id == None:
        return None
    if not hasattr(id, "string"):
        return get_var(id)
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
    elif id.child:
        t = get_var(id.id)
        if type(t) is list:
            return t[len(t)-1][id.child]
        else:
            return t[id.child]
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
    if key[0]=='%':
        return params[key[1:]]
    if key[0]=='$':
        return environment[key[1:]]
    elif '.' in key:
        id = key.split('.')[0]
        child = key.split('.')[1]
        t = get_var(id)
        if type(t) is list:
            return t[len(t)-1][child]
        else:
            return t[child]
    return get_var(key)

def command_runner(commands: list):
    for c in commands:
        if c == "done":
            break
        c.launch()
