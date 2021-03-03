from string import Formatter
import json
from dataclasses import dataclass, field
from typing import List
import asyncio
import importlib, os, pathlib, sys, tempfile, urllib

from .streams import streams, consumers, producers

import mist.action_run

from mist.sdk import (db, get_id, get_key, get_param, watchers, functions, config,
                      watchedInsert, MistAbortException, command_runner, function_runner,
                      execution, environment, ValueContainer, getChildFromVar,
                      get_var, params, resolve_list_dict_reference, MistCallable)
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
class SetCommand:
    parent: object
    key: object
    value: object

    async def run(self, stack):

        if config.debug:
            print(f"-> SetCommand {self.key}")

        # Get the value to be stored
        val = await self.value.value.run(stack) if isinstance(self.value.value, FunctionCall) else await get_id(self.value, stack)

        # Get where to store the value
        if isinstance(self.key, str):
            # Look from the top of the stack for the variable and set the value
            # in the first scope we found. If not found create the variable in
            # the current scope
            scope = stack[-1]
            for s in reversed(stack):
                if self.key in s:
                    scope = s
                    break

            scope[self.key] = val
        elif isinstance(self.key, ListDictReference):
            obj = get_var(self.key.id, stack)
            m = await get_id(self.key.member, stack)
            obj[m] = val
        else:
            raise MistException(f"Unexpected LHS value {type(self.key)}")
        return

@dataclass
class FunctionCall(MistCallable):
    parent: object
    name: str
    args: list
    namedArgs: list
    commands: list
    targetStream: str

    async def run(self, stack):
        if config.debug:
            print(f"-> FunctionCall {self.name}")

        sourceStream = None
        for arg in self.args:
            #if arg.source:
            if isinstance(arg.value, Source):
                sourceStream = await arg.value.getValue(stack)
                break
        for arg in self.namedArgs:
            #if arg.value.source:
            if isinstance(arg.value.value, Source):
                sourceStream = await arg.value.value.getValue(stack)

        if sourceStream or self.targetStream:
            t = asyncio.create_task(function_runner(self.name, stack[:], sourceStream, self.targetStream, self.args, self.namedArgs))
            t.waitingForQueue = False
            if sourceStream:
                streams.createIfNotExists(sourceStream[1:])
                consumers.append(t)
            if self.targetStream:
                streams.createIfNotExists(self.targetStream)
                producers.append(t)
        else:
            result = await function_runner(self.name, stack, sourceStream, self.targetStream, self.args, self.namedArgs, self.commands)
            return result

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
        stack[-1]["MistFunctionResultTmpVariable"] = await get_id(self.value, stack)            

@dataclass
class IncludeCommand:
    parent: object
    files: list

    async def run(self, stack):
        if config.debug:
            print(f"-> Include {self.files}")
        for f in self.files:
            if not (f.endswith(".mist") or f.endswith(".MIST")):
                f += ".mist"
            if not os.path.isfile(f):
                f = str(pathlib.Path(sys.modules['__main__'].__file__).parent.parent) + "/catalog/" + f
            with open(f, "r") as f:
                content = f.read()
                stdout = await mist.action_run.execute_from_text(text=content, fn_params=environment, stack=stack)
                print(stdout, end = '')

@dataclass
class ImportCommand:
    parent: object
    files: list

    async def run(self, stack):
        if config.debug:
            print(f"-> Import {self.files}")
        for py_file in self.files:
            module_name = pathlib.Path(py_file).stem
            if py_file.startswith("http"):
                dest = tempfile.NamedTemporaryFile(suffix=".py")
                destname = dest.name
                sys.path.append(os.path.dirname(destname))
                with urllib.request.urlopen(py_file) as remote:
                    dest.write(remote.read())
                    dest.flush()
                module = importlib.import_module(pathlib.Path(destname).stem)
            else:
                sys.path.append(os.path.dirname(py_file))
                module = importlib.import_module(module_name)
            for fname in dir(module):
                ffunc = getattr(module, fname)
                if fname[0] != "_" and callable(ffunc):
                    name = module_name + fname[0].upper() + fname[1:]
                    functions[name] = {"native": True, "commands": ffunc}

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
class CustomList(ValueContainer):
    parent: object
    components: list

    async def getValue(self, stack):
        return [ await get_id(c, stack) for c in self.components ]

@dataclass
class CustomDict(ValueContainer):
    parent: object
    entries: list

    async def getValue(self, stack):
        return { e.key: await get_id(e.value, stack) for e in self.entries }

@dataclass
class ListDictReference(ValueContainer):
    parent: object
    id: str
    member: object

    async def getValue(self, stack):
        return await resolve_list_dict_reference(self.id, self.member, stack)

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
class IfCommand:
    parent: object
    main: object    # IfCommand (textx)
    elsifs: list    # ElsifCommand (textx)
    default: object # ElseCommand (textx)

    async def run(self, stack):
        # Run the commands of the branch that has a true condition. Evaluate in order, main, all elsifs and default
        if await self.evaluate(self.main.condition, stack):
            await command_runner(self.main.commands, stack)
            return

        for branch in self.elsifs:
            if await self.evaluate(branch.condition, stack):
                await command_runner(branch.commands, stack)
                return

        if self.default:
            await command_runner(self.default.commands, stack)

    async def evaluate(self, condition, stack):
        return bool(await get_id(condition.cond, stack))

@dataclass
class Source(ValueContainer):
    parent: object
    source: str
    sourceIndirect: str

    async def getValue(self, stack):
        if self.source:
            return ":" + self.source
        return ":" + await get_id(self.sourceIndirect, stack)

exports = [DataCommand, SaveListCommand, WatchCommand, IfCommand,
           SetCommand, FunctionCall, ImportCommand,
           FunctionDefinition, IncludeCommand, StringData, ExtParameter,
           EnvVariable, CustomList, CustomDict, VarReference, Source,
           ListDictReference, ReturnCommand]
