import re
import json
import csv
import xml.etree.ElementTree as ET

from dataclasses import dataclass

from jsonpath_ng import parse

from mist.sdk import db, get_id, get_param, stack, config, execution

@dataclass
class BuiltExec:
    parent: object
    command: str
    params: list
    outputs: list
    commands: list

    def run(self):
        printOutputParam = get_param(self.params, "printOutput")
        printOutput = get_id(printOutputParam) if printOutputParam else True

        command = self.command.format(**{
            p.key: get_id(p.value)
            for p in self.params
        })

        if config.debug:
            print( f"-> Exec '{command}'")

        with execution(command) as (executor, in_files, out_files):

            with executor as console_lines:
                for line in console_lines:
                    if config.real_time and config.console_output and printOutput:
                        print(line)

            return {
                "result": executor.status_text(),
                "resultCode": executor.status(),
                "consoleOutput": executor.console_output(),
                "consoleError": executor.stderr_output()
            }



exports = [BuiltExec]
