from textx import metamodel_from_file

from dataclasses import dataclass


@dataclass
class PingCommand:
    parent: object
    ip: str
    consoleRename: str
    commands: list

    def run(self, spaces: int = 0):
        print(f"-> Doing Ping to {self.ip}")
        for c in self.commands:
            c.run()

@dataclass
class DataCommand:
    parent: object
    name: str
    params: list

    def run(self, spaces: int = 0):
        print(f"-> Define data {self.name}")

@dataclass
class CheckCommand:
    parent: object
    var: str
    result: list
    commands: list

    def run(self, spaces: int = 0):
        print(f"-> Check {self.var} is {self.result}")
        for c in self.commands:
            c.run()

@dataclass
class SaveCommand:
    parent: object
    p1: str
    p2: str
    target: str
    targetParams: list

    def run(self, spaces: int = 0):
        print(f"-> Save {self.p1} {self.p2} to {self.target}")

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
