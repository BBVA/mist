Find Open Ports command
=======================

Description
-----------

This command perform a port scan to a target host

Input parameters
----------------

- ip: target IP or dns name
- ports: ports to scan. Ex: "22", "1-65535" "U:53,111,137,T:21-25,80,139,8080,S:9"

Output parameters
-----------------

- result: a string with values "Ok" or "KO". Ok if ping reached target, "OK" otherwise.
- openPorts: a string with a comma separated list of found open ports.
- console: raw text with console output of the command.

Tools and services
------------------

The following commands need to be available in your path command:

- nmap

Examples
--------

Basic: Find open ports (range 0-1023) at localhost and print it on console

.. code-block:: console

    findOpenPorts {
        input {
            ip <= "127.0.0.1"
            ports <= "0-1023"
        }
        output {
            result
            openPorts
            console
        }
        then {
            print openPorts
        }
    }

Advanced: Read a csv file with my hosts, scan (range 0-49151) all ips and write the result to another csv file

.. code-block:: "examples/nmap/myhosts.csv"

    ip,so
    127.0.0.1,linux
    192.168.1.23,windows
    8.8.8.8,unknown

.. code-block:: console

    data myHostsChecked {
        Host
        OpenPorts
    }

    CSVput "examples/nmap/myhosts.csv" => myHosts

    iterate myHosts => host {
        findOpenPorts {
            input {
                ip <= host.ip
                ports <= "0-49151"
            }
            output {
                result
                openPorts
                console
            }
            then {
                put ip openPorts => myHostsChecked
            }
        }
    }
    
    CSVdump myHostsChecked => "myHostsChecked.csv"

