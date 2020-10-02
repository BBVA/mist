import argparse

class _CurrentApp(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(_CurrentApp, self).__init__()

        self["console_output"] = True
        self["real_time"] = True
        self["debug"] = False
        self["persist"] = False
        self["database_path"] = None
        self["simulate"] = False
        self["no_check_tools"] = False

        # self.__dict__ = self

    # def __getitem__(self, key):
    #     return self[key]
    #
    # def __setitem__(self, key, value):
    #     self[key] = value
    #
    # def __setattr__(self, key, value):
    #     self[key] = value
    #
    # def __getattr__(self, item):
    #     return self[item]

    def load_cli_values(self, parsed: argparse.Namespace):
        for k, v in parsed.__dict__.items():
            self[k] = v

config = _CurrentApp()
