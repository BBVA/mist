import csv

from dataclasses import dataclass

from mist.sdk import get_var, db


@dataclass
class WriteCSVCommand:
    parent: object
    fileName: str
    source: str

    def run(self):
        print(f"-> Writing {self.source} => '{self.fileName}'")
        items = get_var(self.source)
        with open(self.fileName, mode='w') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            schema = db.fetch_many(f"PRAGMA table_info({self.source});")
            headers=[]
            for s in schema:
                headers.append(s[1])
            csvWriter.writerow(headers)
            for item in items:
                csvWriter.writerow(item)

exports = [
    WriteCSVCommand
]
