*searchDomains* command
=======================

Description
-----------

This command perform a certificate search at https://crt.sh/ from an origin domain in order to find other related domains.

Input parameters
----------------

- domain: origin dmain to search at https://crt.sh/

Output parameters
-----------------

- result: string with values "Success" or "Error". "Success" if the command has been executed without errors, "Error" otherwise.
- domains: a string with a comma separated list of found domains.
- console: raw text with console output of the command.

Tools and services
------------------

The following commands need to be available in your path command:

- dnsrecon.py

Example
--------

Find related domains from "bbva.com"

.. code-block:: console

    searchDomains {
        input {
            domain <= "bbva.com"
        }
        output {
            result
            domains
            console
        }
        then {
            print domains
        }
    }



