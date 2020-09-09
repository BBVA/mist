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

*exec* command
==============

Description
-----------

This command executes a custom user shell command

Syntax
------

.. code-block:: console

    exec myCustomCommand {
        input {
            param1 = param1value
            ...
        }
        output {
            result
            resultCode
            consoleOutput
            consoleError
        }
        then {
            ...
        }
    }
    

Input parameters
----------------

- myCustomCommand: An string with the shell command I want to execute. You can parametrize it using {} place holders
- paramN: The value of the parameters used in the command

Output parameters
-----------------

- result: a string with values "Success" or "Error". Depending if the command could be executed successfully
- resultCode: the exit code provided after command execution
- consoleOutput: raw text with console standard output of the command.
- consoleError: raw text with console standard error of the command.

Examples
--------

List all files with "txt" extension

.. code-block:: console

    exec "bash -c ls -1 {filter}" {
        input {
            filter = "*.txt"
        }
        output {
            result
            resultCode
            consoleOutput
            consoleError
        }
        then {
            print resultCode
        }
    }

*search* command
================

Description
-----------

Search some regex in a text

Syntax
------

.. code-block:: console

    find regex text {
        output {
            result
            found
        }
        then {
            ...
        }
    }
    

Input parameters
----------------

- regex: a Python3 regex expression
- text: a variable that contains the text to look into.

Output parameters
-----------------

- result: a string with values "Success" or "Error". Depending if the command could be executed successfully
- found: "True" if regex was found. "False" otherwise

Examples
--------

Find a name in a phrase.

.. code-block:: console

    data myData {
        text
    }
    put "Hello, my name is Peter and I like Mist!" => myData
    searchInText "Peter" myData.text {
        output {
            result
            found
        }
        then {
            check found is True {
                print "Peter found"
            }
        }
    }
