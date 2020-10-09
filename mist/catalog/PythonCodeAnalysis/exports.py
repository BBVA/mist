import os
import json

from dataclasses import dataclass

from mist.sdk import get_id, execution, config, MistException


@dataclass
class PythonCodeAnalysisCommand:
    parent: object
    sources: str
    commands: list

    def run(self):
        sources = get_id(self.sources)

        #
        # Check sources path exits
        #
        if not os.path.exists(sources):
            raise MistException("'PythonCodeAnalysis': Sources path not found")

        if config.debug:
            print(f"-> Doing PythonCodeAnalysis for {sources}")

        with execution(f"bandit -r {sources} -f json -o {{outfile-1}}",
                       self.meta) as (executor, in_files, out_files):

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
                content = {}

            issues = []
            for res in content.get("results", []):
                issues.append({
                    "rule": res["test_id"],
                    "code": res["code"],
                    "filename": res["filename"],
                    "severity": res["issue_severity"],
                    "line": res["line_number"]
                })

            return {
                "hasVulnerabilities": True if issues else False,
                "issues": issues,
                "result": executor.status_text(),
                "console": executor.console_output()
            }


exports = [
    PythonCodeAnalysisCommand
]
