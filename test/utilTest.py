from mist.sdk.config import config
from mist.sdk.environment import environment
from mist.sdk.params import params
from mist.sdk.db import db


class MistObj(object):
    def __init__(self, d):
        self.__dict__ = {
                            'id': None,
                            'string': None,
                            'var': None,
                            'param': None,
                            'data': None,
                            'childs': None,
                            'customList': None,
                            'function': None,
                            'source': None}
        self.__dict__.update(d)

def init_mist(mistConfig={'debug': True}, mistEnvironment=None, mistParams=None):

    db.setup() # ?needed?
    if mistConfig:
        config.update(mistConfig)
    if mistEnvironment:
        environment.update(mistEnvironment)
    if mistParams:
        params.update(mistParams)


def create_variable(stack, name, val):
    stack.append({name: val})

def remove_variable(stack, name):
    for d in stack:
        if name in d:
            del d[name]

def clean_variables(stack):
    stack.clear()
    stack.append({"MistBaseNamespace": True})

def create_env_var(stack, name, val):
    environment[name] = val

def remove_env_var(stack, name):
    del environment[name]

def clean_env_vars():
    environment.clear()

def create_mist_param(name, val):
    params[name] = val

def remove_mist_param(name):
    del params[name]

def clean_mist_params():
    params.clear()
