import json
from dataclasses import dataclass

from mist.sdk import stack, get_id, execution, config


@dataclass
class SearchOpenS3BucketsCommand:
    parent: object
    domain: str
    dns: str
    tor: str
    commands: list

    def run(self):
        originDomain = get_id(self.domain)
        dns = get_id(self.dns)
        tor = self.tor.id == 'True' or self.tor.string == 'True'

        if config.debug:
            print(f"-> Doing searchOpenS3Buckets to {originDomain}")

        with execution(
                f"festin {originDomain} -rr {{outfile-1}} {'--tor' if tor else ''} -ds {dns}",
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
            lines = open(out_files['outfile-1'], 'r').readlines() 
            domains, buckets, objects = [],[], []
            for line in lines: 
                json_data = json.loads(line)
                domains.append(json_data["domain"])
                buckets.append(json_data["bucket_name"])
                for object in json_data["objects"]:
                    objects.append(json_data["bucket_name"] + "/" + object)

            return {
                "domain": originDomain,
                "result": executor.status_text(),
                "domains": domains,
                "buckets": buckets,
                "objects": objects,
                "console": executor.console_output()
            }


exports = [
    SearchOpenS3BucketsCommand
]
