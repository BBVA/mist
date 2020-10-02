import csv
from dataclasses import dataclass

from mist.sdk import stack, get_id, execution, config


@dataclass
class SearchDomainsCommand:
    parent: object
    domain: str
    commands: list

    def run(self):
        originDomain = get_id(self.domain)

        if config.debug:
            print(f"-> Doing searchDomains to {originDomain}")

        with execution(
                f"dnsrecon.py -d {originDomain} -t crt -c {{outfile-1}}",
                self.meta
        ) as (executor, in_files, out_files):

            with executor as console_lines:
                if config.real_time and config.console_output:
                    for line in console_lines:
                        print(line)

            if not config.real_time and config.console_output:
                print(executor.console_output())

            #
            # Read result file
            #
            csvfile = open(out_files['outfile-1'])
            reader = csv.reader(csvfile, delimiter=',')

            next(reader) # Discard headers
            domains = [
                row[1]
                for row in reader
            ]

            return {
                "domain": originDomain,
                "result": executor.status_text(),
                "domains": domains,
                "console": executor.console_output()
            }


exports = [
    SearchDomainsCommand
]
