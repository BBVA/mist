# *festin* command

## Description

This command finds open S3 buckets from an origin domain list.

## Concurrency Type

Sync or Async

## Input parameters

- **originDomain**: Origin domain to search S3 buckets.
- **dns**: Dns server to use during execution.
- **tor**: "True" if you want to use Tor network, "False" otherwise.

## Output parameters

- **result**: Boolean, possible values are: True, if the festin command has been
executed without errors, or False otherwise.
- **resultCode**: Integer. Exit code from festin command.
- **consoleOutput**: Raw text with console output from festin command.
- **consoleError**: Raw text with console error from festin command.
- **buckets**: A list of domains, S3 bucket names and objects found.

NOTE: when used as a producer for a queue (Async) every domain found will be sent as soon as found it.

## Tools and services

The following commands need to be available in your command path:

- festin

## Example

Find S3 buckets from "wordpress.com" using Tor network and 212.166.64.1 as dns server.

```text
include "festin"
r = festin("wordpress.com", "212.166.64.1", True)
print(r["buckets"])
```
