import os
import json

from dataclasses import dataclass

from mist.sdk import get_id, execution, config, MistException


@dataclass
class GitLeaksFinderCommand:
    parent: object
    git_path: str
    commands: list

    def run(self):
        git_path = get_id(self.git_path)

        #
        # Check sources path exits
        #
        if not os.path.exists(git_path):
            raise MistException("'GitLeaksFinder': Sources path not found")

        if config.debug:
            print(f"-> Doing PythonCodeAnalysis for {git_path}")

        with execution(f"gitleaks --repo-path \"{git_path}\" --report {{outfile-1}}",
                       self.meta) as (executor, in_files, out_files):

            #
            # Write rules
            #
            # Run !
            with executor as console_lines:
                if config.real_time and config.console_output:
                    for line in console_lines:
                        print(line)

            if not config.real_time and config.console_output:
                print(executor.console_output())

            #
            # Read result file
            #
            try:
                with open(out_files['outfile-1'], "r") as f:
                    content = json.load(f)
            except:
                content = []

            issues = []
            for res in content:
                issues.append({
                    "commit": res["commit"],
                    "repo": res["repo"],
                    "rule": res["offender"],
                    "line": res["lineNumber"]
                })

            return {
                "hasVulnerabilities": True if issues else False,
                "issues": issues,
                "result": executor.status_text(),
                "console": executor.console_output()
            }


exports = [
    GitLeaksFinderCommand
]
