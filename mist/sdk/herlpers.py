from mist.sdk.mapping import mapped
from mist.sdk.stack import stack

def get_var(var):

    if var in stack[len(stack)-1]:
        return stack[len(stack)-1][var]
    if var in mapped:
        return mapped[var]
    return None
