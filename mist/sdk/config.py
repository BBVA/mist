import argparse

class _CurrentApp(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(_CurrentApp, self).__init__()

    def load_cli_values(self, parsed: argparse.Namespace):
        for k, v in parsed.__dict__.items():
            self[k] = v

config = _CurrentApp()
