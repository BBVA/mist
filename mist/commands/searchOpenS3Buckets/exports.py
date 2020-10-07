import json
from dataclasses import dataclass

from mist.sdk import stack, get_id, execution, config


@dataclass
class SearchOpenS3BucketsCommand:
    parent: object
    inputDomains: str
    dns: str
    tor: str
    commands: list

    def run(self):
        dns = get_id(self.dns)
        tor = self.tor.id == 'True' or self.tor.string == 'True'
        inputDomains = get_id(self.inputDomains)
        inputDomains = ' '.join(inputDomains) if type(inputDomains) is list else inputDomains
        
        if config.debug:
            print(f"-> Doing searchOpenS3Buckets to {inputDomains}")

        with execution(
                f"festin {inputDomains} -rr {{outfile-1}} {'--tor' if tor else ''} -ds {dns}",
                # f"echo",
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
            itemsFound = []
            lines = open(out_files['outfile-1'], 'r').readlines() 
            for line in lines:
                json_data = json.loads(line)
                item = {'domain': json_data["domain"], 'bucket': json_data["bucket_name"], 'objects': json_data["objects"] }
                itemsFound.append(item)

            # itemsFound.append({"domain": "hola.com", "bucket": "https://s3.hola.com", "objects": ["a.txt","b.txt"]})
            # itemsFound.append({"domain": "adios.com", "bucket": "https://s3.adios.com", "objects": ["1.txt","2.txt"]})

            return {
                "inputDomains": inputDomains,
                "result": executor.status_text(),
                "itemsFound": itemsFound,
                "console": executor.console_output()
            }


exports = [
    SearchOpenS3BucketsCommand
]
