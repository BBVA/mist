*searchOpenS3Buckets* command
=============================

Description
-----------

This command find open S3 buckets from an origin domain.

Input parameters
----------------

- domain: origin dmain to search
- dns: dns server to use during execution
- tor: "True" if you want to use Tor network 

Output parameters
-----------------

- result: string with values "Success" or "Error". "Success" if the command has been executed without errors, "Error" otherwise.
- domains: a list of found S3 bucket domains.
- buckets: a list of found S3 bucket names.
- objects: a list of found S3 object names.
- console: raw text with console output of the command.

Tools and services
------------------

The following commands need to be available in your path command:

- festin

Example
--------

Find s3 buckets from "wordpress.com" using Tor network and 212.166.64.1 as dns server

.. code-block:: console

    searchOpenS3Buckets {
    input {
        domain <= "wordpress.com"
        dns <= "212.166.64.1"
        tor <= True 
    }
    output {
        result
        domains
        buckets
        objects
        console
    }
    then {
        print domains
        print buckets
        print objects
    }
}
