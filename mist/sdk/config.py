import argparse

class _CurrentApp(dict):

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

    def load_cli_values(self, parsed: argparse.Namespace):
        for k, v in parsed.__dict__.items():
            setattr(self, k, v)

config = _CurrentApp()
