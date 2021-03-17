import argparse

class _CurrentApp(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(_CurrentApp, self).__init__()

    def load_cli_values(self, parsed: argparse.Namespace):
        self.update(parsed.__dict__)

config = _CurrentApp()
