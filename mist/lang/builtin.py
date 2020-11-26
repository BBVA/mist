import re
import json
import csv
import xml.etree.ElementTree as ET

from dataclasses import dataclass

from jsonpath_ng import parse

from mist.sdk import db, get_id, get_param, stack, config, execution, watchedInsert

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

@dataclass
class CSVdumpCommand:
    parent: object
    fileName: str
    source: str

    def run(self):
        if config.debug:
            print(f"-> Writing {self.source} => '{self.fileName}'")

        items = get_id(self.source)
        with open(self.fileName, mode='w') as csvFile:
            csvWriter = csv.writer(csvFile,
                                   delimiter=',',
                                   quotechar='"',
                                   quoting=csv.QUOTE_MINIMAL)
            headers = db.fetch_table_headers(self.source)[1:]
            csvWriter.writerow(headers)
            for row in items:
                row.pop('id', None)
            csvWriter.writerows([
                row.values()
                for row in items
            ])

@dataclass
class CSVputCommand:
    parent: object
    fileName: str
    target: str

    def run(self):
        if config.debug:
            print(f"-> Reading CSV '{self.fileName}' => {self.target}")

        with open(self.fileName) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            # TODO: ADD CSV HEADER?
            headers = next(reader)

            try:
                db.create_table(self.target, headers)

                for row in reader:
                    watchedInsert(self.target, row)

            except Exception as e:
                print(f"Error while creating database: {self.target}")

exports = [BuiltExec, CSVdumpCommand, CSVputCommand]
