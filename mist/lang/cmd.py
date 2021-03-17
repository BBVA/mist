import base64
import os
import re
import abc
import json
import time
import shlex
import hashlib
import tempfile
import subprocess
import asyncio

from typing import Tuple
from functools import lru_cache

from .db import db

input_file_regex = re.compile(r'''(\{)(infile-[\w\.\-\d]+)(\})''')
output_file_regex = re.compile(r'''(\{)(outfile-[\w\.\-\d]+)(\})''')

_DB_TABLE_NAME = "execution"
_DB_TABLE_FIELDS = ("command", "start_time", "end_time", "stdout",
                    "stdout_signature", "stderr", "stderr_signature",
                    "in_files", "out_files")

def _extract_files(text: str, input_or_output: str) -> list:
    if input_or_output == "input":
        regex = input_file_regex
    else:
        regex = output_file_regex

    files = []

    if found := regex.findall(text):
        for _, file_name, _ in found:
            files.append(file_name)

    return files

extract_input_files = lambda x: _extract_files(x, "input")
extract_output_files = lambda x: _extract_files(x, "output")

class Executor(object):

    def __init__(self,
                 command: str,
                 environment: dict,
                 input_files: dict,
                 output_files :dict,
                 interactive: bool):
        self.environment = environment or {}
        self.command = command
        self.input_files = input_files
        self.output_files = output_files
        self.interactive = interactive
        self._console_output = []
        self._console_stderr = []
        self.error_code = None

        self.__create_database__()

    def __create_database__(self):
        db.create_table(
            _DB_TABLE_NAME,
            _DB_TABLE_FIELDS
        )


    def __update_with_results__(self, row_id, end_time):
        if self.stderr_output():
            stderr_signature = hashlib.sha512(
                self.stderr_output().encode()
            ).hexdigest()
        else:
            stderr_signature = ""

        #
        # Read input / output file contents
        #
        input_files = {}
        output_files = {}

        files = (
            (input_files, self.input_files),
            (output_files, self.output_files)
        )

        for (file_results, file_orig) in files:
            for in_file_name, in_file_path in file_orig.items():
                file_results[in_file_name] = {
                    "path": in_file_path,
                    "content": base64.b64encode(open(in_file_path, "rb").read()).decode()
                }

        return db.update(
            row_id,
            _DB_TABLE_NAME,
            {
                "stdout": self.console_output(),
                "stdout_signature": hashlib.sha512(self.console_output().encode()).hexdigest(),
                "stderr": self.stderr_output(),
                "stderr_signature": stderr_signature,
                "end_time": end_time,
                "in_files": json.dumps(input_files),
                "out_files": json.dumps(output_files)
            }
        )

    def __add_to_database__(self, command, start_time):
        return db.insert(
            _DB_TABLE_NAME,
            [
                command,
                str(start_time),
                None,
                None,
                None,
                None,
                None,
                ",".join(self.input_files.values()),
                ",".join(self.output_files.values())
            ]
        )

    @abc.abstractmethod
    def run_ctx(self):
        pass

    async def run(self):
        ctx = await self.run_ctx()
        while 1:
            try:
                next(ctx)
            except StopIteration:
                return

    @lru_cache(1)
    def console_output(self) -> str:
        return "\n".join(self._console_output)

    @lru_cache(1)
    def stderr_output(self) -> str:
        return "\n".join(self._console_stderr)

    def status(self):
        return self.error_code

    def status_text(self):
        return True if self.error_code == 0 else False

    def __enter__(self):
        return self.run_ctx()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class LocalExecutor(Executor):

    def _replace_files_in_command_(self) -> str:
        return self.command.format(**{**self.output_files, **self.input_files})

    async def finish_run(self, row_id, process, wait=True):
        if wait:
            await process.communicate()
        self.error_code = process.returncode
        end_time = time.time()
        self.__update_with_results__(row_id, end_time)

    async def run_ctx(self):

        start_time = time.time()

        new_command = self._replace_files_in_command_()

        run_env = os.environ.copy()
        run_env.update(self.environment)

        command = shlex.split(new_command)

        row_id: str = self.__add_to_database__(new_command, start_time)
        
        # process = await asyncio.create_subprocess_shell(new_command,
        #                            env=run_env,
        #                            stdout=asyncio.subprocess.PIPE,
        #                            stderr=asyncio.subprocess.PIPE,
        #                            universal_newlines=False)
        process = await asyncio.create_subprocess_exec(command[0],
                                   *command[1:],
                                   env=run_env,
                                   stdin=self.interactive,
                                   stdout=asyncio.subprocess.PIPE,
                                   stderr=asyncio.subprocess.PIPE,
                                   universal_newlines=False)

        if self.interactive:
            yield "InteractiveInit", process
            interactive_processes.append((self, row_id, process))
            return
        
        while True:
            output = await process.stdout.readline()
            output = output.decode('utf-8')

            if output == '':
                break

            line = output.strip()
            self._console_output.append(output.strip())

            yield line, process

        while True:
            output = await process.stderr.readline()
            output = output.decode('utf-8')
            if output == '':
                break
            line = output.strip()
            self._console_stderr.append(output.strip())

        await self.finish_run(row_id, process)

class execution(object):

    __db_created__: bool = False

    def __init__(self, command: str, metadata: dict = None, environment: dict = None, interactive=False):
        self.command = command
        self.metadata = metadata or {}
        self.environment = environment or {}
        self.interactive = asyncio.subprocess.PIPE if interactive else None 

        self.input_files = {}
        self.output_files = {}

        self._tmp_files = []

        self._load_files()


    def _load_files(self):

        for via, fn in (
                ("out", extract_output_files), ("in", extract_input_files)
        ):
            for f in fn(self.command):
                tmp_file = tempfile.NamedTemporaryFile()
                self._tmp_files.append(tmp_file)

                if via == "out":
                    self.output_files[f] = tmp_file.name
                else:
                    self.input_files[f] = tmp_file.name

    def __enter__(self) -> Tuple[Executor, dict, dict]:
        executor = LocalExecutor(
            self.command,
            self.environment,
            self.input_files,
            self.output_files,
            self.interactive
        )
        return executor, self.input_files, self.output_files

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        # Destructor
        for f in self._tmp_files:
            f.close()

interactive_processes = []

__all__ = ("execution", interactive_processes)
