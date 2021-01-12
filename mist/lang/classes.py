from string import Formatter
import json
from dataclasses import dataclass, field
from typing import List
import asyncio

from .streams import streams, workers

import mist.action_run

from mist.sdk import db, get_id, get_key, get_param, watchers, functions, config, watchedInsert, MistAbortException, command_runner, function_runner, execution, environment
from mist.sdk.exceptions import MistException
from mist.sdk.stack import stack


@dataclass
class DataCommand:
    parent: object
    name: str
    params: list = field(default_factory=list)

    async def run(self):

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

    async def run(self):
        if config.debug:
            print(f"-> Put to {self.target}")
        fields = None
        if self.params:
            fields = [p for p in self.params]
        values = [
            json.dumps(await get_id(i)) if i.customList or type(await get_id(i)) is list else str(await get_id(i))
            for i in self.sources
        ]
        await watchedInsert(self.target, values, fields=fields)

@dataclass
class SaveListCommand:
    parent: object
    list: str
    selectors: list
    sources: list
    target: str
    params: list

    async def run(self):
        if config.debug:
            print(f"->Put list to {self.target}")

        cols = [c for c in self.params] if self.params else None
        sels = [s for s in self.selectors] if self.selectors else None

        elements = await get_id(self.list)
        if type(elements) is not list:
            raise MistException(f"{self.list} is not a list")

        commons = [ str(await get_id(it)) for it in self.sources ] if self.sources else None

        for el in elements:
            if type(el) is dict:
                values = [ v for v in el.values() ] if sels is None else [ el[sel] for sel in sels ]
            else:
                values = list(str(el))

            if commons is not None:
                values.extend(commons)

            await watchedInsert(self.target, values, fields=cols)

@dataclass
class CheckCommand:
    parent: object
    var: str
    operator: str
    result: list
    commands: list
    elseCommands: list

    async def run(self):
        if config.debug:
            print(f"-> Check that {self.var} is {self.result}")

        # If condition is not met we substitute the check command list with the else command list.
        if (self.operator == 'is') and (await get_id(self.var) != await get_id(self.result)):
            self.commands = self.elseCommands
        elif (self.operator == 'is not') and (await get_id(self.var) == await get_id(self.result)):
            self.commands = self.elseCommands
        return True

@dataclass
class PrintCommand:
    parent: object
    texts: list

    async def run(self):
        if config.debug:
            print(f"-> BuiltPrint")

        print(*([await get_id(s) for s in self.texts]))

@dataclass
class AbortCommand:
    parent: object
    reason: str

    async def run(self):
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

    async def run(self):
        if config.debug:
            print(f"-> Iterate {self.var}")

        res = []

        for index, item in enumerate(await get_id(self.var)):
            res.append({self.name: item, "index": index})

        return res

@dataclass
class WatchCommand:
    parent: object
    var: str
    name: str
    commands: list

    async def run(self):
        if config.debug:
            print(f"-> Watch {self.var}")
        watchers.append({"var": self.var, "name": self.name, "commands": self.commands})

@dataclass
class AppendCommand:
    parent: object
    target: str
    value: str

    async def run(self):
        if config.debug:
            print(f"-> AppendCommand {self.target}")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s[self.target].append(await get_id(self.value))

@dataclass
class SetCommand:
    parent: object
    key: str
    value: str

    async def run(self):
        if config.debug:
            print(f"-> SetCommand {self.key}")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s[self.key] = await get_id(self.value)

@dataclass
class SendCommand:
    parent: object
    value: str

    async def run(self):
        targetStream = await get_key("targetStream")
        value = await get_id(self.value)
        if config.debug:
            print(f"-> SendCommand {targetStream} <= {value}")
        await streams.send(targetStream, value)

@dataclass
class ExposeCommand:
    parent: object
    value: str

    async def run(self):
        if config.debug:
            print(f"-> ExposeCommand {self.value}")
        for i in range(len(stack)-1,0,-1):
            if "MistBaseNamespace" in stack[i]:
                stack[i-1][self.value] = await get_key(self.value)

@dataclass
class FunctionCall:
    parent: object
    name: str
    args: list
    namedArgs: list
    result: str
    commands: list
    targetStream: str
    sourceStream: str

    async def run(self):
        if config.debug:
            print(f"-> FunctionCall {self.name}")
        if self.sourceStream or self.targetStream:
            t = asyncio.create_task(function_runner(self.name, self.sourceStream, self.targetStream, self.args, self.namedArgs))
            workers.append(t)
        else:    
            result = await function_runner(self.name, self.sourceStream, self.targetStream, self.args, self.namedArgs)
            if self.commands:
                stack.append({self.result: result} if self.result else {})
                await command_runner(self.commands)
                stack.pop()

@dataclass
class FunctionDefinition:
    parent: object
    name: str
    args: list
    result: str
    commands: list

    async def run(self):
        if config.debug:
            print(f"-> Function Definition {self.name}")
        functions[self.name] = {"native": False, "commands": self.commands, "args": self.args, "result": self.result}

@dataclass
class IncludeCommand:
    parent: object
    files: list

    async def run(self):
        if config.debug:
            print(f"-> Include {self.files}")
        for f in self.files:
            with open(f, "r") as f:
                content = f.read()
                print(await mist.action_run.execute_from_text(content, environment))
        

exports = [DataCommand, SaveCommand, SaveListCommand, CheckCommand,
           PrintCommand, IterateCommand, WatchCommand, AbortCommand,
           SetCommand, ExposeCommand, AppendCommand, FunctionCall,
           FunctionDefinition, IncludeCommand, SendCommand]
