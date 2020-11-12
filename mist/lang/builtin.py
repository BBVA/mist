import re
import json
import csv
import xml.etree.ElementTree as ET

from dataclasses import dataclass

from jsonpath_ng import parse

from mist.sdk import db, get_id, stack, config, execution, watchedInsert

@dataclass
class BuiltExec:
    parent: object
    command: str
    params: list
    outputs: list
    commands: list

    def run(self):
        command = self.command.format(**{
            p.key: get_id(p.value)
            for p in self.params
        })

        if config.debug:
            print( f"-> Exec '{command}'")

        with execution(command) as (executor, in_files, out_files):

            with executor as console_lines:
                if config.real_time and config.console_output:
                    for line in console_lines:
                        print(line)

            return {
                "result": executor.status_text(),
                "resultCode": executor.status(),
                "consoleOutput": executor.console_output(),
                "consoleError": executor.stderr_output()
            }


@dataclass
class BuiltSearchInText:
    parent: object
    regex: str
    text: str
    outputs: list
    commands: list

    def run(self):
        text = get_id(self.text)

        if config.debug:
            print( f"-> SearchInText '{self.regex}'")

        found = False
        try:
            if re.search(self.regex, text):
                found = True

            result = True
        except Exception as e:
            print(f" Error in 'BuiltSearchInText' -> {e}")
            result = False

        return {
            "regex": self.regex,
            "text": text,
            "result": result,
            "found": found
        }

@dataclass
class BuiltSearchInXML:
    parent: object
    xpath: str
    text: str
    outputs: list
    commands: list

    def run(self):
        text = get_id(self.text)
        if config.debug:
            print( f"-> SearchInXML '{self.xpath}'")

        try:
            root = ET.fromstring(text)
            found = root.findall(self.xpath)
        except Exception as e:
            found = None
            print(f" Error in 'BuiltSearchInXML' -> {e}")

        return {
            "xpath": self.xpath,
            "text": text,
            "result": found is not None,
            "found": [ {"text": e.text, "attributes": e.attrib } for e in found ] if found is not None else []
        }

@dataclass
class BuiltSearchInJSON:
    parent: object
    jsonpath: str
    text: str
    outputs: list
    commands: list

    def run(self):
        text = get_id(self.text)

        if config.debug:
            print( f"-> SearchInJSON '{self.jsonpath}'")

        try:
            json_data = json.loads(text)
            jsonpath_expression = parse(self.jsonpath)
            found = jsonpath_expression.find(json_data)
        except Exception as e:
            found = None
            print(f" Error in 'BuiltSearchInJSON' -> {e}")

        return {
            "xpath": self.jsonpath,
            "text": text,
            "result": found is not None,
            "found": found is not None and len(found) > 0,
            "value": found[0].value if found else None
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

exports = [BuiltExec, BuiltSearchInText, BuiltSearchInXML, BuiltSearchInJSON, CSVdumpCommand, CSVputCommand]
