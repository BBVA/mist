from textx import metamodel_from_file

from dataclasses import dataclass
import subprocess

stack = []
mapped = {}

@dataclass
class PingCommand:
    parent: object
    ip: str
    resultRename: str
    consoleRename: str
    commands: list

    def run(self, spaces: int = 0):
        print(f"-> Doing Ping to {self.ip}")
        process = subprocess.Popen(['ping', '-c 1', self.ip], 
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
                    "result": result,
                    "console": console
                })
                if self.resultRename != "":
                    mapped[self.resultRename] = result
                if self.consoleRename != "":
                    mapped[self.consoleRename] = console
                break
        #print(f"stack before then {stack}")
        for c in self.commands:
            c.run()
        stack.pop()
        #print(f"stack after then {stack}")
        #print(f"mapped after then {mapped}")

@dataclass
class DataCommand:
    parent: object
    name: str
    params: list

    def run(self, spaces: int = 0):
        print(f"-> Define data {self.name}")

def getVar(var):
    #print(f"Find Var: {var}")
    if var in stack[len(stack)-1]:
        return stack[len(stack)-1][var]
    if var in mapped:
        return mapped[var]
    return None

@dataclass
class CheckCommand:
    parent: object
    var: str
    result: list
    commands: list

    def run(self, spaces: int = 0):
        print(f"-> Check that {self.var} is {self.result}")
        if getVar(self.var) == self.result:
            for c in self.commands:
                c.run()

@dataclass
class SaveCommand:
    parent: object
    sources: list
    target: str
    params: list

    def run(self, spaces: int = 0):
        print(f"-> Save {self.sources} to {self.target}({self.params})")

def process_scan(model):
    print(f"Target: {model.target}")
    for action in model.actions:
        action.run()


def interpret(model):
    # model is an instance of Program
    for c in model.commands:
        c.run()

def main():
    hacking_mm = metamodel_from_file(
        'ping.tx',
        classes=[
            PingCommand,
            DataCommand,
            CheckCommand,
            SaveCommand
        ])
    hacking_model = hacking_mm.model_from_file(
        'ping.mist'
    )

    interpret(hacking_model)


if __name__ == '__main__':
    main()
