import csv

from dataclasses import dataclass

from mist.sdk import get_id, db, config


@dataclass
class DumpCSVCommand:
    parent: object
    fileName: str
    source: str

    def run(self):
        if config.debug:
            print(f"-> Writing {self.source} => '{self.fileName}'")

        items = get_id(self.source)
        with open(self.fileName, mode='w') as csvFile:
            csvWriter = csv.writer(csvFile,
                                   delimiter=',',
                                   quotechar='"',
                                   quoting=csv.QUOTE_MINIMAL)
            headers = db.fetch_table_headers(self.source)
            csvWriter.writerow(headers)
            csvWriter.writerows({
                row.values()
                for row in items
            })

exports = [
    DumpCSVCommand
]
