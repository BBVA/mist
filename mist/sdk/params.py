import argparse

class _InputParams(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(_InputParams, self).__init__(*args, **kwargs)

    def load_cli_values(self, parsed: argparse.Namespace):
        if len(parsed.OPTIONS) > 1:

            for _tuple in parsed.OPTIONS[1:]:
                k, v = _tuple.split("=")
                self[k] = v


params = _InputParams()
