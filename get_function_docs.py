from inspect import getmembers, isfunction

import mist.lang.function as mist_func


for f in getmembers(mist_func, isfunction):
    print(f[1].__doc__)
