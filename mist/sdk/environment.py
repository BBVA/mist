import os

class _EnvironmentVars(dict):

    def __init__(self, *args, **kwargs):
        super(_EnvironmentVars, self).__init__()

        self.update(os.environ)

    def __getitem__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]


environment = _EnvironmentVars()
