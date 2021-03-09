# *PythonCodeAnalysis* command

## Description

Performs security code analysis on Python code.

## Concurrency Type

Sync

## Input parameters

- **sources**: Path of Python source code.

## Output parameters

- **result**: Boolean, possible values are: True, if the gitleaks command has been
executed without errors and not issues detected, or False otherwise.
- **resultCode**: Integer. Exit code from gitleaks command.
- **consoleOutput**: Raw text with console output from gitleaks command.
- **consoleError**: Raw text with console error from gitleaks command.
- **issues**: List of issues found by the analyzer.

## Tools and services

The following commands need to be available in your command path:

- bandit

## Examples

**Basic**: Find vulnerabilities in python code ay current directory

``` text
include "gitLeaksFinder"
r = gitLeaksFinder("./")
print(r)
```
