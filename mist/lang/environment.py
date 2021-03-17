import os

class _EnvironmentVars(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(_EnvironmentVars, self).__init__()

        self.update(os.environ)


environment = _EnvironmentVars()
