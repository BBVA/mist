from dataclasses import dataclass, field
from mist.sdk import db, get_var, get_id, stack, watchers, config, watchedInsert

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
        if config.debug:
            print(f"-> Put to {self.target}")
        fields = None
        if len(self.params)>0:
            fields = [p for p in self.params]

        values = [
            get_var(i.id) if i.id else i.string if i.string else i.data
            for i in self.sources
        ]

        watchedInsert(self.target, values, fields=fields)

@dataclass
class CheckCommand:
    parent: object
    var: str
    result: list
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Check that {self.var} is {self.result}")
        if get_var(self.var) == self.result:
            for c in self.commands:
                c.run()

@dataclass
class BuiltPrint:
    parent: object
    text: str

    def run(self):
        if config.debug:
            print(f"-> BuiltPrint")
        #print(get_id(self.text), end='')
        print(get_id(self.text))

@dataclass
class IterateCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Iterate {self.var}")

        for index, item in enumerate(get_var(self.var)):
            stack.append({self.name: item, "index": index})
            for c in self.commands:
                c.run()
            stack.pop()

@dataclass
class WatchCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Watch {self.var}")
        watchers.append({"var": self.var, "name": self.name, "commands": self.commands})

exports = [DataCommand, SaveCommand, CheckCommand, BuiltPrint, IterateCommand, WatchCommand]
