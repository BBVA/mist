from xml.dom import minidom
from dataclasses import dataclass

from mist.sdk import stack, get_id, execution, config


@dataclass
class FindOpenPortsCommand:
    parent: object
    ip: str
    ports: str
    commands: list

    def run(self):
        ip = get_id(self.ip)

        if config.debug:
            print(f"-> Doing findOpenPorts to {ip}")

        with execution(
                f"nmap -p {self.ports} --open {ip} -oX {{outfile-1}}",
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
            mydoc = minidom.parse(out_files['outfile-1'])
            items = mydoc.getElementsByTagName('port')

            openPorts = [
                elem.attributes['portid'].value
                for elem in items
            ]

            return {
                "ip": ip,
                "ports": self.ports,
                "result": executor.status_text(),
                "openPorts": openPorts,
                "console": executor.console_output()
            }


exports = [
    FindOpenPortsCommand
]
