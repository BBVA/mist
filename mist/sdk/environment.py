import os

class _EnvironmentVars(dict):

    def __init__(self, *args, **kwargs):
        super(_EnvironmentVars, self).__init__()

        self.update(os.environ)


environment = _EnvironmentVars()
