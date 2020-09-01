from textx import metamodel_from_file

from dataclasses import dataclass
import subprocess
import sqlite3

con = sqlite3.connect(':memory:')

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
        sqlCommand = f"CREATE TABLE {self.name} (id integer PRIMARY KEY AUTOINCREMENT, "
        for i in self.params:
            sqlCommand += f"{i} text,"
        sqlCommand = sqlCommand[:-1]
        sqlCommand += ")"
        print(f"-> Define data: {sqlCommand}")
        cursorObj = con.cursor()
        cursorObj.execute(sqlCommand)
        con.commit()

@dataclass
class SaveCommand:
    parent: object
    sources: list
    target: str
    params: list

    def run(self, spaces: int = 0):
        sqlCommand = f"INSERT INTO {self.target} "
        if len(self.params)>0:
            sqlCommand += "("
            for i in self.params:
                sqlCommand += f"{i},"
            sqlCommand = sqlCommand[:-1]
            sqlCommand += ") VALUES(" 
        else:
            sqlCommand += "VALUES(null, "
        for i in self.sources:
            value = getVar(i.id) if i.id != "" else i.string
            sqlCommand += f"'{value}',"
        sqlCommand = sqlCommand[:-1]
        sqlCommand += ")"
        print(f"-> Save: {sqlCommand}")
        cursorObj = con.cursor()
        cursorObj.execute(sqlCommand)
        con.commit()

@dataclass
class DumpCommand:
    parent: object
    target: str

    def run(self, spaces: int = 0):
        print(f"-> Dump {self.target}")
        cursorObj = con.cursor()
        sqlCommand = f"SELECT * FROM {self.target}"
        cursorObj.execute(sqlCommand)
        rows = cursorObj.fetchall()
        for row in rows:
            print(row)

def getVar(var):
    # print(f"Find Var: {var}")
    # print(f"Stack: {stack}")
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
            SaveCommand,
            DumpCommand,
        ])
    hacking_model = hacking_mm.model_from_file(
        'ping.mist'
    )

    interpret(hacking_model)


if __name__ == '__main__':
    main()
