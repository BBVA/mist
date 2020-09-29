from dataclasses import dataclass

from mist.sdk import stack, get_id, execution, config


@dataclass
class PingCommand:
    parent: object
    ip: str
    commands: list

    def run(self):
        ip = get_id(self.ip)

        if config.debug:
            print(f"-> Doing Ping to {ip}")

        with execution(f"ping -c1 -W 1 {ip}", self.meta) as (executor, _, _):
            executor.run()

            if config.console_output:
                print(executor.console_output())

            return {
                "ip": ip,
                "result": executor.status_text(),
                "console": executor.console_output()
            }

        #     stack.append({
        #         "ip": ip,
        #         "result": executor.status_text,
        #         "console": executor.console_output
        #     })
        #
        # for c in self.commands:
        #     c.run()
        # stack.pop()

exports = [
    PingCommand
]
