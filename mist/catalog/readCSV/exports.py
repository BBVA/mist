import csv

from dataclasses import dataclass

from mist.sdk import mapped


@dataclass
class ReadCSVCommand:
    parent: object
    fileName: str
    target: str

    def run(self):
        print(f"-> Reading CSV '{self.fileName}' => {self.target}")
        with open(self.fileName) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            headers = next(reader)
            rows = []
            for row in reader:
                item = {}
                for i,h in enumerate(headers):
                    item[h]=row[i]
                rows.append(item)
            mapped.set(self.target, rows)

exports = [
    ReadCSVCommand
]
