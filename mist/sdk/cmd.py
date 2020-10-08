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

    __db_created__ = False

    def __init__(self,
                 command: str,
                 environment: dict,
                 input_files: dict,
                 output_files :dict):
        self.environment = environment or {}
        self.command = command
        self.input_files = input_files
        self.output_files = output_files
        self._console_output = []
        self._console_stderr = []
        self.error_code = None

        self.__create_database__()

    def __create_database__(self):
        if not Executor.__db_created__:
            db.create_table(
                _DB_TABLE_NAME,
                _DB_TABLE_FIELDS
            )

            Executor.__db_created__ = True

    def __update_with_results__(self, row_id, end_time):
        if self.stderr_output():
            stderr_signature = hashlib.sha512(
                self.stderr_output().encode()
            ).hexdigest()
        else:
            stderr_signature = None

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

    def run(self):
        ctx = self.run_ctx()
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

    def run_ctx(self):

        start_time = time.time()

        new_command = self._replace_files_in_command_()

        run_env = os.environ.copy()
        run_env.update(self.environment)

        command = shlex.split(new_command)

        row_id: int = self.__add_to_database__(new_command, start_time)

        process = subprocess.Popen(command,
                                   env=run_env,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        while True:
            output = process.stdout.readline()

            if (error_code := process.poll()) is not None and output == '':
                self.error_code = error_code
                break

            line = output.strip()
            self._console_output.append(output.strip())

            yield line

        self._console_stderr.extend(process.stderr.readlines())

        end_time = time.time()

        #
        # Save execution information
        #
        self.__update_with_results__(row_id, end_time)

class execution(object):

    __db_created__: bool = False

    def __init__(self, command: str, metadata: dict = None, environment: dict = None):
        self.command = command
        self.metadata = metadata or {}
        self.environment = environment or {}

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
            self.output_files
        )

        return executor, self.input_files, self.output_files

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        # Destructor
        for f in self._tmp_files:
            f.close()

def main():
    command = "nmap -p 80,90,1028 -v -oN {outfile-1} 127.0.0.1"
    with execution(command) as (executor, in_files, out_files):


        with executor as lines:
            for x in lines:
                print(x)

        print(executor.status())
        print(executor.console_output())

        with open(out_files["outfile-1"], "r") as f:
            content = f.read()

            print(content)

if __name__ == '__main__':
    main()

__all__ = ("execution",)
