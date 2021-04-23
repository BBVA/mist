from inspect import getmembers, isfunction

import mist.lang.function as mist_func


for f in getmembers(mist_func, isfunction):
    print(f[1].__doc__)


print(f"""
## Utility functions

Mist, in addition to all the previous functions, provides developers with some
utility functions to handle with strings, dictionaries and lists that are
imported directly from Python.

You can see the documentation about all these funcions in [Python's documentation](https://docs.python.org/3/library/stdtypes.html)

### String utility functions

The following functions are available: {', '.join([ f"[{f[0]}](https://docs.python.org/3/library/stdtypes.html#str.{f[0]})" for f in getmembers(str) if f[0][0] != "_" and callable(f[1]) ])}.

### Dictionary utility functions

The following functions are available: {', '.join([ f"[{f[0]}](https://docs.python.org/3/library/stdtypes.html#str.{f[0]})" for f in getmembers(dict) if f[0][0] != "_" and callable(f[1]) ])}.

### List utility functions

The following functions are available: {', '.join([ f"[{f[0]}](https://docs.python.org/3/library/stdtypes.html#str.{f[0]})" for f in getmembers(list) if f[0][0] != "_" and callable(f[1]) ])}.

""")
