**put** command
===============

Description
-----------
 
This command put data to the knowledge base.
The number of parameter must match with the data structure fields

Syntax
------

.. code-block:: console

    put IDorString [IDorString] [IDorString] ... => targetId
    put IDorString [IDorString] [IDorString] ... => targetId(field1 field2 field3...)

Parameters
----------

- IdorString: An string or an id with the name of the source local variable.
- targetId: data structure id of the knowledge base
- fieldX: optionally, you can chose the order of the fields to put

Examples
--------

.. code-block:: console

    data myHosts {
        ip
        so
    }

    put "127.0.0.1" "linux" => myHosts
    put "windows" "192.168.1.23" => myHosts(so ip)
    put "8.8.8.8" "unknown" => myHosts

    data myIps {
        ip
    }

    iterate myHosts => host {
        put host.ip => MyIps
    }

**print** command
=================

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


**iterate** command
===================

Description
-----------
 
This command iterate over a data list

Syntax
------

.. code-block:: console

    iterate myList => item {
        ...
    }

Parameters
----------

- myList: An id with the name of the source list: local variable or knowledge base id.
- item: the name of the local variable to map every item

Examples
--------

.. code-block:: console

    data myHosts {
        ip
        so
    }

    put "127.0.0.1" "linux" => myHosts
    put "windows" "192.168.1.23" => myHosts(so ip)
    put "8.8.8.8" "unknown" => myHosts

    iterate myHosts => host {
        print host.ip
    }
