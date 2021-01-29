from string import Formatter
import json
from dataclasses import dataclass, field
from typing import List
import asyncio

from .streams import streams, consumers, producers

import mist.action_run

from mist.sdk import db, get_id, get_key, get_param, watchers, functions, config, watchedInsert, MistAbortException, command_runner, function_runner, execution, environment, ValueContainer, getChildFromVar, get_var, params
from mist.sdk.exceptions import MistException, MistUndefinedVariableException

@dataclass
class DataCommand:
    parent: object
    name: str
    params: list = field(default_factory=list)

    async def run(self, stack):

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

    async def run(self, stack):
        if config.debug:
            print(f"-> Put to {self.target}")
        fields = None
        if self.params:
            fields = [p for p in self.params]
        values = [
            json.dumps(await get_id(i, stack)) if i.value.__class__.__name__ == 'CustomList' or type(await get_id(i, stack)) is list else str(await get_id(i, stack))
            for i in self.sources
        ]
        await watchedInsert(self.target, stack, values, fields=fields)

@dataclass
class SaveListCommand:
    parent: object
    list: str
    selectors: list
    sources: list
    target: str
    params: list

    async def run(self, stack):
        if config.debug:
            print(f"->Put list to {self.target}")

        cols = [c for c in self.params] if self.params else None
        sels = [s for s in self.selectors] if self.selectors else None

        elements = await get_id(self.list, stack)
        if type(elements) is not list:
            raise MistException(f"{self.list} is not a list")

        commons = [ str(await get_id(it, stack)) for it in self.sources ] if self.sources else None

        for el in elements:
            if type(el) is dict:
                values = [ v for v in el.values() ] if sels is None else [ el[sel] for sel in sels ]
            else:
                values = list(str(el))

            if commons is not None:
                values.extend(commons)

            await watchedInsert(self.target, stack, values, fields=cols)

@dataclass
class CheckCommand:
    parent: object
    var: str
    operator: str
    result: list
    commands: list
    elseCommands: list

    async def run(self, stack):
        if config.debug:
            print(f"-> Check that {self.var} is {self.result}")

        # If condition is not met we substitute the check command list with the else command list.
        left = await get_id(self.var, stack)
        right = await get_id(self.result, stack)
        if self.operator == 'is' and left != right:
            self.commands = self.elseCommands
        elif self.operator == 'is not' and left == right:
            self.commands = self.elseCommands
        return True

@dataclass
class PrintCommand:
    parent: object
    texts: list

    async def run(self, stack):
        if config.debug:
            print(f"-> BuiltPrint")

        print(*([await get_id(s, stack) for s in self.texts]))

@dataclass
class AbortCommand:
    parent: object
    reason: str

    async def run(self, stack):
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

    async def run(self, stack):
        if config.debug:
            print(f"-> Iterate {self.var}")

        res = []

        for index, item in enumerate(await get_id(self.var, stack)):
            res.append({self.name: item, "index": index})

        return res

@dataclass
class WatchCommand:
    parent: object
    var: str
    name: str
    commands: list

    async def run(self, stack):
        if config.debug:
            print(f"-> Watch {self.var}")
        watchers.append({"var": self.var, "name": self.name, "commands": self.commands})

@dataclass
class AppendCommand:
    parent: object
    target: str
    value: str

    async def run(self, stack):
        if config.debug:
            print(f"-> AppendCommand {self.target}")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s[self.target].append(await get_id(self.value, stack))

@dataclass
class SetCommand:
    parent: object
    key: str
    value: str

    async def run(self, stack):

        if config.debug:
            print(f"-> SetCommand {self.key}")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s[self.key] = await get_id(self.value, stack)

@dataclass
class SendCommand:
    parent: object
    value: str

    async def run(self, stack):
        try:
            targetStream = await get_key("targetStream", stack)
        except MistUndefinedVariableException as e:
            if config.debug:
                print(f"-> Ignoring SendCommand because there is not targetStream")
            return
        value = await get_id(self.value, stack)
        if config.debug:
            print(f"-> SendCommand {targetStream} <= {value}")
        await streams.send(targetStream, value)

@dataclass
class ExposeCommand:
    parent: object
    value: str

    async def run(self, stack):
        if config.debug:
            print(f"-> ExposeCommand {self.value}")
        for i in range(len(stack)-1,0,-1):
            if "MistBaseNamespace" in stack[i]:
                stack[i-1][self.value] = await get_key(self.value, stack)

@dataclass
class FunctionCall:
    key: str
    parent: object
    name: str
    args: list
    namedArgs: list
    #result: str
    commands: list
    targetStream: str

    async def run(self, stack):
        if config.debug:
            print(f"-> FunctionCall {self.name}")

        sourceStream = None
        for arg in self.args:
            #if arg.source:
            if isinstance(arg.value, ValueContainer):
                sourceStream = await arg.value.getValue(stack)
                break
        for arg in self.namedArgs:
            #if arg.value.source:
            if isinstance(arg.value.value, ValueContainer):
                sourceStream = await arg.value.value.getValue(stack)

        if sourceStream or self.targetStream:
            t = asyncio.create_task(function_runner(self.name, stack[:], sourceStream, self.targetStream, self.args, self.namedArgs))
            if sourceStream:
                streams.createIfNotExists(sourceStream)
                consumers.append(t)
            if self.targetStream:
                streams.createIfNotExists(self.targetStream)
                producers.append(t)
        else:
            result = await function_runner(self.name, stack, sourceStream, self.targetStream, self.args, self.namedArgs, self.commands)
            if self.key:
                for s in reversed(stack):
                    if "MistBaseNamespace" in s:
                        s[self.key] = result

@dataclass
class FunctionDefinition:
    parent: object
    name: str
    args: list
    commands: list

    async def run(self, stack):
        if config.debug:
            print(f"-> Function Definition {self.name}")
        functions[self.name] = {"native": False, "commands": self.commands, "args": self.args}

@dataclass
class ReturnCommand:
    parent: object
    value: str

    async def run(self, stack):
        if config.debug:
            print(f"-> ReturnCommand")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s["result"] = await get_id(self.value, stack)

@dataclass
class IncludeCommand:
    parent: object
    files: list

    async def run(self, stack):
        if config.debug:
            print(f"-> Include {self.files}")
        for f in self.files:
            with open(f, "r") as f:
                content = f.read()
                # TODO: pass stack
                print(await mist.action_run.execute_from_text(content, environment))

# Create the classes StringData, ExtParameter, EnvVariable, FunctionInlineCall, CustomList, VarReference and Source, all implementing ValueContainer and containing the corresponding code in herlpers.get_id
@dataclass
class StringData(ValueContainer):
    parent: object
    data: str

    async def getValue(self, stack):
        return self.data

@dataclass
class ExtParameter(ValueContainer):
    parent: object
    param: str

    async def getValue(self, stack):
        return params[self.param]

@dataclass
class EnvVariable(ValueContainer):
    parent: object
    var: str

    async def getValue(self, stack):
        return environment[self.var]

@dataclass
class FunctionInlineCall(ValueContainer):
    parent: object
    name: str
    namedArgs: list
    args: list

    async def getValue(self, stack):
        return await function_runner(self.name, stack, None, None, self.args, self.namedArgs )

@dataclass
class CustomList(ValueContainer):
    parent: object
    components: list

    async def getValue(self, stack):
        return [ await get_id(c, stack) for c in self.components ]

@dataclass
class VarReference(ValueContainer):
    parent: object
    id: str
    childs: list

    async def getValue(self, stack):
        if self.childs:
            return getChildFromVar(get_var(self.id, stack), self.childs)
        else:
            return get_var(self.id, stack)

@dataclass
class Source(ValueContainer):
    parent: object
    source: str

    async def getValue(self, stack):
        return ":" + self.source

exports = [DataCommand, SaveCommand, SaveListCommand, CheckCommand,
           PrintCommand, IterateCommand, WatchCommand, AbortCommand,
           SetCommand, ExposeCommand, AppendCommand, FunctionCall,
           FunctionDefinition, IncludeCommand, StringData, ExtParameter,
           EnvVariable, FunctionInlineCall, CustomList, VarReference, Source,
           SendCommand, ReturnCommand]
