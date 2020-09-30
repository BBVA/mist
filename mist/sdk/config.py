import argparse

class _CurrentApp(dict):

    def __init__(self, *args, **kwargs):
        super(_CurrentApp, self).__init__()

        self.__dict__["console_output"] = True
        self.__dict__["real_time"] = True
        self.__dict__["debug"] = False
        self.__dict__["persist"] = False
        self.__dict__["database_path"] = None
        self.__dict__["simulate"] = False

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

    def load_cli_values(self, parsed: argparse.Namespace):
        for k, v in parsed.__dict__.items():
            setattr(self, k, v)

config = _CurrentApp()
