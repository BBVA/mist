import argparse

class _InputParams(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(_InputParams, self).__init__(*args, **kwargs)


params = _InputParams()
