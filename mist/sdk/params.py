import argparse

class _InputParams(dict):

    def __init__(self, *args, **kwargs):
        super(_InputParams, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

    def load_cli_values(self, parsed: argparse.Namespace):
        if len(parsed.OPTIONS) > 1:

            for _tuple in parsed.OPTIONS[1:]:
                k, v = _tuple.split("=")
                self.__dict__[k] = v


params = _InputParams()
