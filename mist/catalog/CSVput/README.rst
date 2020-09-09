*CSVput* command
================

Description
-----------
 
This command reads a CSV file and put all the data into the knowledge base

Syntax
------

.. code-block:: console

    CSVput "sourceFile.csv" => target


Parameters
----------

- "sourceFile.csv": An string with the path and name of the source CSV file
  (CSV header is mandatory, and delimiter must be a comma)
- target: An id with the target name in the knowledge base

Examples
--------

Read a csvFile and iterate over it printing some of its content.

.. code-block:: "examples/nmap/myhosts.csv"

    ip,so
    127.0.0.1,linux
    192.168.1.23,windows
    8.8.8.8,unknown

.. code-block:: console

    CSVput "examples/nmap/myhosts.csv" => myHosts

    iterate myHosts => host {
        print host.ip
    }
