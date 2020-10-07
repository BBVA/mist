*PythonCodeAnalysis* command
=======================

Description
-----------

Perform security code analysis for Python code

Input parameters
----------------

- sources: path of Python source code

Output parameters
-----------------

- result: string with values "Success" or "Error". "Success" if the command has been executed without errors, "Error" otherwise.
- console: raw text with console output of the command.
- issues: list of issues found by analyzer

Tools and services
------------------

The following commands need to be available in your path command:

- bandit

Examples
--------

Basic: Find vulnerabilities in a python code

.. code-block:: console

    PythonCodeAnalysis {
    input {
        sources <= %sourcesPath
    }
    output {
        hasVulnerabilities
        issues
        result
        console
    }
    then {
        check result is Error {
            Abort "Issues detected!"
        }
        check result is Success {
            print "Code is clean and safe"
        }
    }
}

Where `%sourcesPath` is a input parameter
