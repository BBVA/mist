import os

class _EnvironmentVars(dict):

    def __init__(self, *args, **kwargs):
        super(_EnvironmentVars, self).__init__()

        self.__dict__.update(os.environ)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]


environment = _EnvironmentVars()
