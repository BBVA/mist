CSVdump command
===============

Description
-----------
 
This command write a data structure of the knowledge base into a CSV file

Syntax
------

.. code-block:: console

    CSVdump data => "targetFile.csv"

Parameters
----------

- data: An id with the name of the source data structure in the knowledge base
- "targetFile.csv": An string with the path and name of the target CSV file

Examples
--------

Define a data structure, fill it with some content, and dump it to a CSV file.

.. code-block:: console

    data myHosts {
        ip
        so
    }

    put "127.0.0.1" "linux" => myHosts
    put "192.168.1.23" "windows" => myHosts
    put "8.8.8.8" "unknown" => myHosts

    CSVdump myHosts => "myHosts.csv"
