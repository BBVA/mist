from mist.sdk.mapping import mapped
from mist.sdk.stack import stack
from mist.sdk import db

def get_var(var):
    if len(stack)>0 and var in stack[len(stack)-1]:
        return stack[len(stack)-1][var]
    elif hasattr(mapped,var):
        return mapped.get(var)
    return db.fetch_many(f"SELECT * FROM {var}")

def get_id(id):
    if id.string != "":
        return id.string
    elif id.child != "":
        return get_var(id.id)[id.child]
    elif id.index > 0:
        return get_var(id.id)[id.index]
    return get_var(id.id)
    