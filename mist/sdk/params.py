import argparse

class _InputParams(dict):

    def __init__(self):
        super().__init__()

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
