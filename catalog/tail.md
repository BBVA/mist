# *tail* command

## Description

This command is a wrapper for tail command.
It will read a file line by line and send each line to a queue.
The command will terminate when read an specific EOF token.

## Concurrency Type

Async

## Input parameters

- **file**: String. File to read.
- **endline**: String. EOF line token.

## Output parameters

Each line will be send to the target queue

## Tools and services

The following commands need to be available in your command path:

- tail

## Example

Read file domains.txt, send every line to queue "l". Stop reading when "*END*" is read.

``` text
include "tail"
tail("domains.txt","*END*") => l
print(: l)
```
