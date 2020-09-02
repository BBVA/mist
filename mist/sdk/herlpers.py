from mist.sdk.mapping import mapped
from mist.sdk.stack import stack

def get_var(var):

    if len(stack)>0 and var in stack[len(stack)-1]:
        return stack[len(stack)-1][var]
    return mapped.get(var)
