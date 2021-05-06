from string import Formatter
import json
from dataclasses import dataclass, field
from typing import List
import asyncio
import importlib, os, pathlib, sys, tempfile, urllib, uuid
import shutil
import inspect

from .streams import streams, consumers, producers

import mist.action_run

from mist.lang.environment import environment
from mist.lang.cmd import execution
from mist.lang.function import functions
from mist.lang.config import config
from mist.lang.exceptions import MistMissingBinaryException, MistAbortException, MistException, MistUndefinedVariableException, MistPipelineException
from mist.lang.herlpers import MistCallable, get_var, params, command_runner, function_runner, get_id, get_key, get_param, getChildFromVar, resolve_list_dict_reference, ValueContainer

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
class SetCommand:
    parent: object
    key: object
    value: object
    
    def __repr__(self):
        return str(f"{self.key} = {self.value}")

    async def run(self, stack):

        if config.debug:
            print(f"[DEBUG] " + self.__repr__())

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
class IDorSTRING():
    parent: object
    value: object

    def __repr__(self):
        return str(self.value)

@dataclass
class FunctionCall(MistCallable):
    parent: object
    method: str  
    args: list
    namedArgs: list
    commands: list
    targetStream: str = None

    def __repr__(self):
        return str(f"{'.'.join([self.method.id] + self.method.childs)}({'.'.join([str(i) for i in self.args])})")

    async def run(self, stack):
        if config.debug:
            print(f"[DEBUG] " + self.__repr__())

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
            t = asyncio.create_task(function_runner(self.method, stack[:], sourceStream, self.targetStream, self.args, self.namedArgs))
            t.waitingForQueue = False
            if sourceStream:
                streams.createIfNotExists(sourceStream[1:])
                consumers.append(t)
            if self.targetStream:
                for s in self.targetStream:
                    streams.createIfNotExists(s)
                producers.append(t)
        else:
            result = await function_runner(self.method, stack, sourceStream, self.targetStream, self.args, self.namedArgs, self.commands)
            return result

@dataclass
class FunctionDefinition:
    parent: object
    name: str
    args: list
    commands: list
    targetStreams: list

    async def run(self, stack):
        if config.debug:
            print(f"[DEBUG] FunctionDefinition {self.name}")
            
        functions[self.name] = {"native": False, "commands": self.commands, "args": self.args}

@dataclass
class ReturnCommand:
    parent: object
    value: str

    async def run(self, stack):
        if config.debug:
            print(f"[DEBUG] return {self.value}")
        stack[-1]["MistFunctionResultTmpVariable"] = await get_id(self.value, stack)            

@dataclass
class IncludeCommand:
    parent: object
    files: list

    async def run(self, stack):
        if config.debug:
            print(f"[DEBUG] Include {self.files}")
        for f in self.files:
            commandName = f
            if not (f.endswith(".mist") or f.endswith(".MIST")):
                f += ".mist"
            if not os.path.isfile(f):
                if os.path.isfile(mist.action_run.language_tools.mist_file_base_dir + "/" + f):
                    f = mist.action_run.language_tools.mist_file_base_dir + "/" + f
                else:
                    f = str(pathlib.Path(sys.modules['mist'].__file__).parent) + "/catalog/" + f
            with open(f, "r") as f:
                content = f.read()
                requiredText = "# Tools:"                
                i = content.find(requiredText)
                if i>=0:
                    tools = content[i+len(requiredText):].split("\n")[0].split(",")
                    for t in tools:
                        bin = t.strip()
                        if not shutil.which(bin):
                            raise MistMissingBinaryException(
                            f"Command '{commandName}' need '{bin}' to be "
                            f"executed. Please install them."
                        )
                stdout = await mist.action_run.execute_from_text(text=content, fn_params=environment, stack=stack)
                print(stdout, end = '')

@dataclass
class ImportCommand:
    parent: object
    files: list

    async def run(self, stack):
        if config.debug:
            print(f"[DEBUG] Import {self.files}")
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
                if not os.path.isfile(py_file):
                    py_file = mist.action_run.language_tools.mist_file_base_dir + "/" + py_file
                sys.path.append(os.path.dirname(py_file))
                module = importlib.import_module(module_name)
            for fname in dir(module):
                ffunc = getattr(module, fname)
                if fname[0] != "_" and callable(ffunc):
                    #name = module_name + fname[0].upper() + fname[1:]
                    name = fname
                    functions[name] = {"native": True, "commands": ffunc, "async": inspect.iscoroutinefunction(ffunc)}

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

    def __repr__(self):
        return str(self.param)

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

    def __repr__(self):
        return str(f"{[str(i) for i in self.components]}")

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

    def __repr__(self):
        return str(f"{self.id}[{self.member}]")

    async def getValue(self, stack):
        return await resolve_list_dict_reference(self.id, self.member, stack)

@dataclass
class VarReference(ValueContainer):
    parent: object
    id: str
    childs: list

    def __repr__(self):
        return str(f"v'{'.'.join([self.id] + self.childs)}")

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

    def __repr__(self):
        return f"{self.source}{self.sourceIndirect if self.sourceIndirect else ''}"

    async def getValue(self, stack):
        if self.source:
            return ":" + self.source
        return ":" + await get_id(self.sourceIndirect, stack)

@dataclass
class ObjectWithValue:
    value: object

    def __repr__(self):
        return f"{self.value}"

@dataclass
class PipeNext:
    value: object
    nextVal: object

@dataclass
class PipeCommand(MistCallable):
    parent: object
    left: object
    right: object

    def __repr__(self):
        return f"=> {self.left[0]} " + (f"{self.right}" if self.right else "")

    async def run(self, stack):
        if config.debug:
            print(f"[DEBUG] " + self.__repr__())

        left = self.left
        right = self.right

        # CASES
        # Case 1 : left = variable or value or queue, right=function
        # Case 2 : left = variable or value, right=direct queue (id) or indirect queue (source)
        # Case 3 : left = function, right=None
        # Case 4 : left = function, right=queue
        # Case 5 : left = function, right=function      
        # Case 6 : left = queue, right=None (META CASE FOR STOP CONDITION)
        while left:
            if isinstance(left[0].value, FunctionCall):
                if not right: # Case 3
                    pass
                elif isinstance(right.left[0].value, VarReference): # Case 4 
                    left[0].value.targetStream = [i.value.id for i in right.left]
                elif isinstance(right.left[0].value, FunctionCall): # Case 5
                    tmpStream = str(uuid.uuid4())
                    left[0].value.targetStream = [tmpStream]
                    right.left[0].value.args.insert(0, ObjectWithValue(Source(self, tmpStream, None)))
                else:
                    raise MistPipelineException()
                await left[0].value.launch(stack)
            else: # Case 1 or 2
                if not right: # Case 6: Do nothing and stop
                    return
                leftVal = None
                try:
                    leftVal = await get_id(left[0], stack) # Left is variable or value
                except: # Left is queue
                    left[0].value = Source(self, left[0].value.id, None)
                if isinstance(right.left[0].value, FunctionCall): # Case 1
                    right.left[0].value.args.insert(0, left[0])
                elif isinstance(right.left[0].value, VarReference) or isinstance(right.left[0].value, Source): # Case 2
                    value = right.left[0].value.id if isinstance(right.left[0].value, VarReference) else get_var(right.left[0].value.sourceIndirect, stack)
                    realTargetStreams = None
                    for s in reversed(stack):
                        if 'targetStream' in s:
                            realTargetStreams = s['targetStream']
                            break
                    if realTargetStreams: 
                        metaTargetStream = value
                        fcall = right.left[0].parent
                        while not isinstance(fcall, FunctionDefinition):
                            fcall = fcall.parent
                        metaTargetStreams = fcall.targetStreams
                        i = metaTargetStreams.index(metaTargetStream)
                        await streams.send(realTargetStreams[i], leftVal)
                    else:
                        await streams.send(value, leftVal)
                else:
                    raise MistPipelineException()
                
            if right:
                left = right.left
                right = right.right
            else:
                left = None

exports = [ IfCommand, SetCommand, FunctionCall, ImportCommand,
           FunctionDefinition, IncludeCommand, StringData, ExtParameter,
           EnvVariable, CustomList, CustomDict, VarReference, Source,
           ListDictReference, ReturnCommand, PipeCommand, IDorSTRING]
