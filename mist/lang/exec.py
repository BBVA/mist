import subprocess
import tempfile

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

exports = [BuiltExec]
