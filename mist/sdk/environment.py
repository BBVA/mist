import os


class _EnvironmentVars(dict):

    def __init__(self):
        super().__init__()
        self.__dict__.update(os.environ)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]


environment = _EnvironmentVars()
