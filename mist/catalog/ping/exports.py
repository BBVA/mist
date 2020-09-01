import subprocess

from dataclasses import dataclass

from mist.sdk import stack, mapped


@dataclass
class PingCommand:
    parent: object
    ip: str
    resultRename: str
    consoleRename: str
    commands: list

    def run(self, spaces: int = 0):
        print(f"-> Doing Ping to {self.ip}")
        process = subprocess.Popen(['ping', '-c 1', '-W 1', self.ip],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
        while True:
            output = process.stdout.readline()
            console = output
            print(output.strip())
            return_code = process.poll()
            if return_code is not None:
                print('RETURN CODE', return_code)
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    print(output.strip())
                    console = console + output
                result = "Ok" if return_code == 0 else "Error"

                stack.append({
                    "ip": self.ip,
                    "result": result,
                    "console": console
                })
                if self.resultRename != "":
                    mapped.set(self.resultRename, result)
                if self.consoleRename != "":
                    mapped.set(self.consoleRename, console)
                break
        #print(f"stack before then {stack}")
        for c in self.commands:
            c.run()
        stack.pop()
        #print(f"stack after then {stack}")
        #print(f"mapped after then {mapped}")


exports = [
    PingCommand
]
