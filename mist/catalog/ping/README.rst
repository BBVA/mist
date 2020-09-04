Ping command
============

Description
-----------

This command perform a ping to a target

Input parameters
----------------

- ip: target IP

Output parameters
-----------------

- result: string with values "Ok" or "KO". Ok if ping reached target, "OK" otherwise.
- console: raw text with console output of the command

Tools and services
------------------

Ping need to be available in your path command:

- ping

Examples
--------

Pinging local host and store host status in *myHost* bucket

.. code-block:: console

    data myHosts {
        Host
        Status
    }

    ping {
        input {
            ip <= "127.0.0.1"
        }
        output {
            result
            console
        }
        then {
            check result is Ok {
                put ip 'Up' => myHosts
            }
            check result is Error {
                put ip 'Down' => myHosts(Host Status)
            }
        }
    }
