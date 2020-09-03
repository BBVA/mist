import csv

from dataclasses import dataclass

from mist.sdk import get_var, get_id, db


@dataclass
class DumpCSVCommand:
    parent: object
    fileName: str
    source: str

    def run(self):
        print(f"-> Writing {self.source} => '{self.fileName}'")
        items = get_var(self.source)
        with open(self.fileName, mode='w') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            headers = db.get_headers(self.source)
            csvWriter.writerow(headers)
            for item in items:
                t = [(v) for k, v in item.items()] 
                csvWriter.writerow(t)

exports = [
    DumpCSVCommand
]
