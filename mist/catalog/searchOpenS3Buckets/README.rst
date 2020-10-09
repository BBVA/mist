*searchOpenS3Buckets* command
=============================

Description
-----------

This command find open S3 buckets from an origin domain list.

Input parameters
----------------

- inputDomains: origin domain list to search
- dns: dns server to use during execution
- tor: "True" if you want to use Tor network 

Output parameters
-----------------

- result: string with values "Success" or "Error". "Success" if the command has been executed without errors, "Error" otherwise.
- outputDomains: a list of found S3 bucket domains.
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
        inputDomains <= "wordpress.com"
        dns <= "212.166.64.1"
        tor <= True 
    }
    output {
        result
        outputDomains
        buckets
        objects
        console
    }
    then {
        print outputDomains
        print buckets
        print objects
    }
}
