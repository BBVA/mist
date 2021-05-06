from mist.lang.config import config
from mist.lang.environment import environment
from mist.lang.params import params


_mistStack = []
class MistObj(object):
    def __init__(self, d):
        self.__dict__ = { 'value': None }
        self.__dict__.update(d)

def init_mist(mistConfig={'debug': False}, mistEnvironment=None, mistParams=None):

    if mistConfig:
        config.update(mistConfig)
    if mistEnvironment:
        environment.update(mistEnvironment)
    if mistParams:
        params.update(mistParams)

    clean_variables()

def get_mistStack():
    return _mistStack

def create_variable(name, val):
    _mistStack.append({name: val})

def remove_variable(name):
    for d in _mistStack:
        if name in d:
            del d[name]

def clean_variables():
    _mistStack.clear()
    _mistStack.append({"MistBaseNamespace": True})

def create_env_var(name, val):
    environment[name] = val

def remove_env_var(name):
    del environment[name]

def clean_env_vars():
    environment.clear()

def create_mist_param(name, val):
    params[name] = val

def remove_mist_param(name):
    del params[name]

def clean_mist_params():
    params.clear()
