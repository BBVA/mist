# *filterRepeated* command

## Description

To use with queues. This command filter repeated values in a given list. And send non repeated values.

## Input parameters

- **v**: Any. Input value to check
- **values**: List where all values will be saved. (With no repetitions)

## Output parameters

Non repeated items will be sent.

## Examples

Filer repeated domains at input queue "domains" and output non repeated to queu "nonRepeatedDomains".

``` text
domainProcessed = []
filterRepeated(:domains, domainProcessed) => nonRepeatedDomains
```
