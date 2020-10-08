*GitLeaksFinder* command
========================

Description
-----------

Find sensitive information in Git repositories

Input parameters
----------------

- gitPath: path of Git repositories

Output parameters
-----------------

- hasVulnerabilities: True if vulnerabilities found False otherwise.
- result: string with values "Success" or "Error". "Success" if the command has been executed without errors, "Error" otherwise.
- console: raw text with console output of the command.
- issues: list of issues found by analyzer

Issues results format:

.. code-block:: json

    [
        {
            "commit": {COMMIT-ID},
            "repo": {REPO NAME},
            "rule": {RULE NAME},
            "line": {LINE NUMBER}
        }
    ]

Tools and services
------------------

The following commands need to be available in your path command:

- gitleaks

Examples
--------

.. code-block:: console

    GitLeaksFinder {
        input {
            git_path <= %gitPath
        }
        output {
            hasVulnerabilities
            issues
            result
            console
        }
        then {

            check hasVulnerabilities is True {
                Abort "Code has vulnerabilities"
            }
            check hasVulnerabilities is False {
                print "Code is clean and safe"
            }
        }
    }

Where `%gitPath` is a input parameter
