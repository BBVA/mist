from mist.sdk.stack import stack
from mist.sdk import db

def get_var(var):
    if len(stack)>0 and var in stack[len(stack)-1]:
        return stack[len(stack)-1][var]
    return db.fetch_table_as_dict(var)

def get_id(id):
    #print(f"get_id id={id.id} string={id.string} child={id.child}")
    if not hasattr(id, "string"):
        return get_var(id)
    if id.string != "":
        return id.string
    elif id.data != "":
        return id.data
    elif id.child != "":
        all = get_var(id.id)
        if isinstance(all, list):
            return all[len(all)-1][id.child]
        else:
            return all[id.child]
    return get_var(id.id)
