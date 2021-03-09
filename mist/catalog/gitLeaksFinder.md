# *gitLeaksFinder* command

## Description

Finds sensitive information in Git repositories.

## Concurrency Type

Sync

## Input parameters

- **gitPath**: Path of Git repositories.

## Output parameters

- **result**: Boolean, possible values are: True, if the gitleaks command has been
executed without errors and not issues detected, or False otherwise.
- **resultCode**: Integer. Exit code from gitleaks command.
- **consoleOutput**: Raw text with console output from gitleaks command.
- **consoleError**: Raw text with console error from gitleaks command.
- **issues**: List of issues found by analyzer.

Issues contains an array of objects with the following information:

``` json
  [
    {
      "commit": {COMMIT-ID},
      "repo": {REPO NAME},
      "rule": {RULE NAME},
      "line": {LINE NUMBER}
    }
  ]
```

## Tools and services

The following commands need to be available in your command path:

- gitleaks

## Examples

Find sensitive information in git repository at current directory

``` text
include "gitLeaksFinder"
r = gitLeaksFinder("./")
print(r)
```

Example output:

```text
{'result': False, 'resultCode': 1, 'consoleOutput': '\x1b[36mINFO\x1b[0m[2021-02-17T16:46:02+01:00] report written to /var/folders/vt/0gyg50fx3_q3nn0dwhmjgynh0000gp/T/tmpuwfs8mvr\n\x1b[33mWARN\x1b[0m[2021-02-17T16:46:02+01:00] 1 leaks detected. 9 commits scanned in 1 second 738 milliseconds 202 microseconds', 'consoleError': '', 'issues': [{'line': '          "current_key": "XXXXXXXXXXXXXXXXXXX"', 'lineNumber': 24, 'offender': 'XXXXXXXXXXXXXXXXXXX', 'commit': 'XXXXXXXXXXXXXXXXXXX', 'repo': 'XXXXXXXXXXXXXXXXXXX', 'rule': 'Google API key', 'commitMessage': 'Version 1.0.2\n', 'author': 'XXXXXXXXXXXXXXXXXXX', 'email': 'XXXXXXXXXXXXXXXXXXX', 'file': 'google-services.json', 'date': '2019-08-25T14:14:34+02:00', 'tags': 'key, Google', 'operation': 'addition'}]}
```
