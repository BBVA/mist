from dataclasses import dataclass, field

from mist.sdk import db, get_var


@dataclass
class DataCommand:
    parent: object
    name: str
    params: list = field(default_factory=list)

    def run(self, spaces: int = 0):

        table_params = [
            f"{param} text"
            for param in self.params
        ]

        db.create_table(self.name, table_params)

@dataclass
class SaveCommand:
    parent: object
    sources: list
    target: str
    params: list

    def run(self, spaces: int = 0):
        fields = None
        if len(self.params)>0:
            fields = [p for p in self.params]

        values = [
            get_var(i.id) if i.id else i.string
            for i in self.sources
        ]

        db.insert(self.target, values, fields=fields)

@dataclass
class DumpCommand:
    parent: object
    target: str

    def run(self, spaces: int = 0):

        print(f"-> Dump {self.target}")
        for row in db.fetch_many(f"SELECT * FROM {self.target}"):
            print(row)


@dataclass
class CheckCommand:
    parent: object
    var: str
    result: list
    commands: list

    def run(self, spaces: int = 0):
        print(f"-> Check that {self.var} is {self.result}")
        if get_var(self.var) == self.result:
            for c in self.commands:
                c.run()


exports = [DataCommand, SaveCommand, DumpCommand, CheckCommand]
