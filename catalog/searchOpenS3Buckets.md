# *searchOpenS3Buckets* command

## Description

This command finds open S3 buckets from an origin domain list.

## Input parameters

- **originDomain**: Origin domain to search S3 buckets.
- **dns**: Dns server to use during execution.
- **tor**: "True" if you want to use Tor network, "False" otherwise.

## Output parameters

- **result**: Boolean, possible values are: True, if the command has been
executed without errors, or False otherwise.
- **resultCode**: Integer. Exit code from dnsrecon command.
- **consoleOutput**: Raw text with console output from dnsrecon command.
- **consoleError**: Raw text with console error from dnsrecon command.
- **buckets**: A list of domains, S3 bucket names and objects found.

## Tools and services

The following commands need to be available in your command path:

- festin

## Example

Find S3 buckets from "wordpress.com" using Tor network and 212.166.64.1 as dns server.

```text
include "searchOpenS3Buckets"
r = searchOpenS3Buckets("wordpress.com", "212.166.64.1", True)
print(r["buckets"])
```
