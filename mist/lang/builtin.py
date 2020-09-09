import subprocess
import re
import xml.etree.ElementTree as ET

from dataclasses import dataclass, field

from mist.sdk import db, get_var, get_id, stack


@dataclass
class BuiltExec:
    parent: object
    command: str
    params: list
    commands: list

    def run(self):
        command = self.command
        for p in self.params:
            command = command.replace("{" + p.key + "}", p.value)
        print( f"-> Exec '{command}'")
        process = subprocess.Popen(command.split(" "),
                           text=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)
        while True:
            consoleOutput = process.stdout.readline()
            consoleError = process.stderr.readline()
            return_code = process.poll()
            if return_code is not None:
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    consoleOutput = consoleOutput + output
                for output in process.stderr.readlines():
                    consoleError = consoleError + output    
                stack.append({
                    "result": "Success" if return_code == 0 else "Error",
                    "resultCode": return_code,
                    "consoleOutput": consoleOutput,
                    "consoleError": consoleError
                })
                break
        for c in self.commands:
            c.run()
        stack.pop()

@dataclass
class BuiltSearchInText:
    parent: object
    regex: str
    text: str
    commands: list

    def run(self):
        text = get_id(self.text)
        print( f"-> SearchInText '{self.regex}'")
        found = "False"
        try:
            found = re.search(self.regex, text)
            if found != None:
                found = "True"
            result = "Success"
        except:
            result = "Error"

        stack.append({
            "regex": self.regex,
            "text": text,
            "result": result,
            "found": found
        })
        for c in self.commands:
            c.run()
        stack.pop()

@dataclass
class BuiltSearchInXML:
    parent: object
    xpath: str
    text: str
    commands: list

    def run(self):
        text = get_id(self.text)
        print( f"-> SearchInXML '{self.xpath}'")
        try:
            root = ET.fromstring(text)
            items = root.findall(self.xpath)
            result = "Success"
        except Exception as e:
            print(f"-> {e}")
            result = "Error"

        stack.append({
            "xpath": self.xpath,
            "text": text,
            "result": result,
            "found": "True" if len(items) > 0 else "False",
            "value": items[0].text
        })
        for c in self.commands:
            c.run()
        stack.pop()


exports = [BuiltExec, BuiltSearchInText, BuiltSearchInXML]
