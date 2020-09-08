import subprocess

from dataclasses import dataclass

from mist.sdk import stack, get_id


@dataclass
class PingCommand:
    parent: object
    ip: str
    commands: list

    def run(self):
        ip = get_id(self.ip)
        print(f"-> Doing Ping to {ip}")
        process = subprocess.Popen(['ping', '-c 1', '-W 1', ip],
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
                result = "Success" if return_code == 0 else "Error"
                stack.append({
                    "ip": ip,
                    "result": result,
                    "console": console
                })
                break
        for c in self.commands:
            c.run()
        stack.pop()

exports = [
    PingCommand
]
