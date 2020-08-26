from textx import metamodel_from_file

from dataclasses import dataclass


@dataclass
class For:
    parent: object
    from_data: str
    tmp_var: str
    commands: list

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}do for ({self.from_data}) -> ({self.tmp_var})")
        for c in self.commands:
            c.run()


@dataclass
class Parallel:
    parent: object
    commands: list

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}-> Doing in parallel")


@dataclass
class ScanCommand:
    parent: object
    target: str
    actions: list
    result: str

    def run(self, spaces: int = 0):
        print(f"-> Doing nmap -> {self.result}")
        for cmd in self.actions:
            cmd.run(spaces + 5)


@dataclass
class SQLMapCommand:
    parent: object
    target: str
    actions: list
    result: str

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}doing sqlmap -> {self.result}")
        for cmd in self.actions:
            cmd.run(spaces + 1)


@dataclass
class WhenAction:
    parent: object
    condition: str
    when_commands: list

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}When condition: {self.condition}")
        for cmd in self.when_commands:
            cmd.run(spaces + 2)


@dataclass
class BuiltExec:
    parent: object
    command: str

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}running command: {self.command}")

    def __repr__(self):
        return f"< exec '{self.command}'>"


@dataclass
class BuiltPrint:
    parent: object
    text: str

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}{self.text}")

    def __repr__(self):
        return f"< print '{self.text}'>"


@dataclass
class BuiltCall:
    parent: object
    function: str
    params: list

    def run(self, spaces: int = 0):
        print(f"{' ' * spaces}Calling function '{self.function}'")


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
        'hacking.tx',
        classes=[
            BuiltExec,
            BuiltPrint,
            WhenAction,
            ScanCommand,
            SQLMapCommand,
            For,
            Parallel,
            BuiltCall
        ])
    hacking_model = hacking_mm.model_from_file(
        'hacking-basic.rbt'
    )

    interpret(hacking_model)


if __name__ == '__main__':
    main()
