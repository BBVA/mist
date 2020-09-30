from typing import List

from mist.sdk.stack import stack
from mist.sdk.db import db
from mist.sdk.config import config
from mist.sdk.watchers import watchers
from mist.sdk.environment import environment
from mist.sdk.params import params

def get_var(var, as_list):
    #print(f"get_var {var}")
    if stack and var in stack[len(stack)-1]:
        v = stack[len(stack)-1][var]
        if type(v) is list and not as_list:
            return ','.join(v)
        return v
    return db.fetch_table_as_dict(var)

def get_id(id, as_list=False):
    # print(f"get_id id={id.id} string={id.string} child={id.child} var={id.var} param={id.param}")
    if not hasattr(id, "string"):
        return get_var(id, as_list)
    if id.var:
        return environment[id.var]
    if id.param:
        return params[id.param]
    if id.string:
        return id.string
    elif id.data:
        return id.data
    elif id.child:
        all = get_var(id.id, as_list)
        if type(all) is list:
            return all[len(all)-1][id.child]
        else:
            return all[id.child]
    return get_var(id.id, as_list)

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
                c.run()
            stack.pop()
