import subprocess
import tempfile
from xml.dom import minidom

from dataclasses import dataclass

from mist.sdk import stack, mapped, get_var


@dataclass
class FindOpenPortsCommand:
    parent: object
    ip: str
    ports: str
    openPortsRename: str
    consoleRename: str
    commands: list

    def run(self, spaces: int = 0):
        ip = self.ip.string if self.ip.id == "" else get_var(self.ip.id)
        if isinstance(ip, list): 
            ip = ip[0]
        print(f"-> Doing findOpenPorts to {ip}")
        tmpFile = tempfile.NamedTemporaryFile()
        tmpFile.close()
        print(tmpFile.name)
        process = subprocess.Popen(['nmap', '-p', self.ports, '--open', ip, '-oX', tmpFile.name],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
        while True:
            output = process.stdout.readline()
            console = output
            print(output.strip())
            return_code = process.poll()
            if return_code is not None:
                print('RETURN CODE', return_code)
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    print(output.strip())
                    console = console + output
                result = "Ok" if return_code == 0 else "Error"
                #Parse xml output to find ports
                mydoc = minidom.parse(tmpFile.name)
                items = mydoc.getElementsByTagName('port')
                openPorts = []
                for elem in items:
                    openPorts.append(elem.attributes['portid'].value)                

                stack.append({
                    "ip": ip,
                    "ports": self.ports,
                    "result": result,
                    "openPorts": ','.join(openPorts),
                    "console": console
                })
                if self.openPortsRename != "":
                    mapped.set(self.openPortsRename, openPorts)
                if self.consoleRename != "":
                    mapped.set(self.consoleRename, console)
                break
        for c in self.commands:
            c.run()
        stack.pop()


exports = [
    FindOpenPortsCommand
]
