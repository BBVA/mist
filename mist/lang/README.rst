Print command
=============

Description
-----------
 
This command write an string, a local variable or a data structure of the knowledge base on console

Syntax
------

.. code-block:: console

    print IDorString

Parameters
----------

- IdorString: An string or an id with the name of the source local variable or data structure.

Examples
--------

.. code-block:: console

    print "Program init"

    data myHosts {
        ip
        so
    }

    put "127.0.0.1" "linux" => myHosts
    put "192.168.1.23" "windows" => myHosts
    put "8.8.8.8" "unknown" => myHosts

    print myHosts

    iterate myHosts => host {
        print host.ip
    }

TODO: put, iterate