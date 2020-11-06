from string import Formatter
import json
from dataclasses import dataclass, field
from typing import List

from mist.sdk import db, get_id, get_key, watchers, functions, config, watchedInsert, MistAbortException
from mist.sdk.stack import stack

@dataclass
class DataCommand:
    parent: object
    name: str
    params: list = field(default_factory=list)

    def run(self):

        table_params = [
            f"{param} text"
            for param in self.params
        ]

        db.create_table(self.name, table_params)

@dataclass
class SaveCommand:
    parent: object
    sources: list
    target: str
    params: list

    def run(self):
        if config.debug:
            print(f"-> Put to {self.target}")
        fields = None
        if self.params:
            fields = [p for p in self.params]
        values = [
            json.dumps(get_id(i)) if i.customList or type(get_id(i)) is list else str(get_id(i))
            for i in self.sources
        ]
        watchedInsert(self.target, values, fields=fields)

@dataclass
class CheckCommand:
    parent: object
    var: str
    result: list
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Check that {self.var} is {self.result}")
        if get_id(self.var) == get_id(self.result):
            return True

@dataclass
class BuiltPrint:
    parent: object
    texts: list

    def run(self):
        if config.debug:
            print(f"-> BuiltPrint")

        def proc(s):
            s = get_id(s)
            if type(s) != str:
               return s
            pairs = [(i[1],get_key(i[1])) for i in Formatter().parse(s) if i[1] is not None]
            for k,v in pairs: 
                s = s.replace('{' + k + '}',str(v),1)
            return s

        print(*([proc(s) for s in self.texts]))

@dataclass
class BuiltAbort:
    parent: object
    reason: str

    def run(self):
        if self.reason:
            reason = self.reason
        else:
            reason = "Abort reached"

        raise MistAbortException(reason)

@dataclass
class IterateCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Iterate {self.var}")

        res = []

        for index, item in enumerate(get_id(self.var)):
            res.append({self.name: item, "index": index})

        return res

@dataclass
class WatchCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Watch {self.var}")
        watchers.append({"var": self.var, "name": self.name, "commands": self.commands})

@dataclass
class IDorSTRING:
    parent: object
    data: str
    id: str
    string: str
    child: str
    var: str
    param: str
    customList: list
    # TODO: check var and params


@dataclass
class FunctionDefinition:
    parent: object
    var: str
    params: list
    commands: list

    def run(self):
        if config.debug:
            print(f"-> FunctionDefinition {self.var}")
        functions.append({"var": self.var, "params": self.params, "commands": self.commands})


@dataclass
class FunctionCall:
    parent: object
    var: str
    params: list

    def run(self):
        if config.debug:
            print(f"-> FunctionCall {self.var}")
        for f in functions:
            if f["var"] == self.var:
                d = {}
                for i,k in enumerate(f["params"]):
                    d[k] = get_id(self.params[i])
                stack.append(d)
                for c in f["commands"]:
                    c.run()
                stack.pop()
                

exports = [DataCommand, SaveCommand, CheckCommand, BuiltPrint,
           IterateCommand, WatchCommand, IDorSTRING, BuiltAbort,
           FunctionDefinition, FunctionCall]
