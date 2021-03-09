# *searchDomains* command

## Description

This command performs a certificate search at https://crt.sh/ for an origin
domain in order to find other related domains.

## Concurrency Type

Sync or Async

## Input parameters

- **originDomain**: Origin domain to search for at https://crt.sh/.

## Output parameters

- **result**: Boolean, possible values are: True, if the dnsrecon command has been
executed without errors, or False otherwise.
- **resultCode**: Integer. Exit code from dnsrecon command.
- **domains**: A list of domains found. This output will also be send to a queue if requiered.
- **consoleOutput**: Raw text with console output from dnsrecon command.
- **consoleError**: Raw text with console error from dnsrecon command.

NOTE: when used as a producer for a queue (Async) every domain found will be sent as soon as found it.

## Tools and services

The following commands need to be available in your command path:

- dnsrecon.py

## Example

Find related domains for "bbva.com" and print result

``` text
include "searchDomains"
r = searchDomains("bbva.com")
print(r)
```
