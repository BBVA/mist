import os
import re
import abc
import time
import shlex
import tempfile
import subprocess

from typing import Tuple
from functools import lru_cache

from .db import db

input_file_regex = re.compile(r'''(\{)(infile-[\w\.\-\d]+)(\})''')
output_file_regex = re.compile(r'''(\{)(outfile-[\w\.\-\d]+)(\})''')

_DB_TABLE_NAME = "execution"
_DB_TABLE_FIELDS = ("command", "start_time", "end_time", "stdout", "stderr",
                    "in_file", "out_files")

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
        return "Success" if self.error_code == 0 else "Error"

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
        db.insert(
            _DB_TABLE_NAME,
            [
                new_command,
                str(start_time),
                str(end_time),
                self.console_output(),
                self.stderr_output(),
                ",".join(self.input_files.values()),
                ",".join(self.output_files.values())
            ]
        )

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
