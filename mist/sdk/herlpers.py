from mist.sdk.stack import stack
from mist.sdk import db

def get_var(var):
    if len(stack)>0 and var in stack[len(stack)-1]:
        return stack[len(stack)-1][var]
    return db.fetch_table_as_dict(var)

def get_id(id):
    #print(f"get_id id={id.id} string={id.string} child={id.child}")
    if id.string != "":
        return id.string
    elif id.child != "":
        return get_var(id.id)[id.child]
    return get_var(id.id)
    