from dataclasses import dataclass, field

from mist.sdk import db, get_var, get_id, stack


@dataclass
class DataCommand:
    parent: object
    name: str
    params: list = field(default_factory=list)

    def run(self):

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

    def run(self):
        fields = None
        if len(self.params)>0:
            fields = [p for p in self.params]

        values = [
            get_var(i.id) if i.id else i.string
            for i in self.sources
        ]

        db.insert(self.target, values, fields=fields)

@dataclass
class CheckCommand:
    parent: object
    var: str
    result: list
    commands: list

    def run(self):
        print(f"-> Check that {self.var} is {self.result}")
        if get_var(self.var) == self.result:
            for c in self.commands:
                c.run()

@dataclass
class BuiltPrint:
    parent: object
    text: str

    def run(self):
        if self.text.id == "":
            print(self.text.string)
        else:
            print(get_id(self.text))

@dataclass
class IterateCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        print(f"-> Iterate {self.var}")
        for index,item in enumerate(get_var(self.var)):
            stack.append({self.name: item, "index": index})
            for c in self.commands:
                c.run()
            stack.pop()
            

exports = [DataCommand, SaveCommand, CheckCommand, BuiltPrint, IterateCommand]
