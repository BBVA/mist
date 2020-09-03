import csv

from dataclasses import dataclass

from mist.sdk import db


@dataclass
class PutCSVCommand:
    parent: object
    fileName: str
    target: str

    def run(self):
        print(f"-> Reading CSV '{self.fileName}' => {self.target}")
        with open(self.fileName) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            headers = next(reader)
            try:
                db.create_table(self.target, headers)
            except:
                pass
            for row in reader:
                db.insert(self.target, row)

exports = [
    PutCSVCommand
]
