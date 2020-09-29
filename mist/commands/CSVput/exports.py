import csv

from dataclasses import dataclass

from mist.sdk import db, config, watchedInsert


@dataclass
class PutCSVCommand:
    parent: object
    fileName: str
    target: str

    def run(self):
        if config.debug:
            print(f"-> Reading CSV '{self.fileName}' => {self.target}")

        with open(self.fileName) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            # TODO: ADD CSV HEADER?
            headers = next(reader)

            try:
                db.create_table(self.target, headers)

                for row in reader:
                    watchedInsert(self.target, row)

            except Exception as e:
                print(f"Error while creating database: {self.target}")

exports = [
    PutCSVCommand
]
