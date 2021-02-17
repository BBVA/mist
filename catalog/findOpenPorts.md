# *findOpenPorts* command

## Description

This command performs a port scan to a target host.

## Input parameters

- **ip**: String. Target IP or dns name.
- **ports**: String. Ports to scan, one, a range or a list of ports giving, optionally,
the protocol (U=UDP, T=TCP, S=SYN scan). Ex: "22", "1-65535", "U:53,111,137,T:21-25,80,139,8080,S:9".

## Output parameters

- **result**: Boolean, possible values are: True, if the nmap command has been
executed without errors, or False otherwise.
- **resultCode**: Integer. Exit code from nmap command.
- **consoleOutput**: Raw text with console output from nmap command.
- **consoleError**: Raw text with console error from nmap command.
- **openPorts**: A list of open ports found.

## Tools and services

The following commands need to be available in your command path:

- nmap

## Examples

Find open ports among a range (0-9000) at localhost and print them
out on console.

``` text
include "findOpenPorts"
r = findOpenPorts("127.0.0.1", "0-9000")
print(r)
```

Expected output:

```text
{'result': True, 'resultCode': 0, 'consoleOutput': 'Starting Nmap 7.80 ( https://nmap.org ) at 2021-02-17 11:48 CET\nNmap scan report for localhost (127.0.0.1)\nHost is up (0.00017s latency).\n\nPORT     STATE SERVICE\n631/tcp  open  ipp\n8021/tcp open  ftp-proxy\n\nNmap done: 1 IP address (1 host up) scanned in 0.03 seconds', 'consoleError': '', 'openPorts': [{'port': '631', 'protocol': 'tcp'}, {'port': '8021', 'protocol': 'tcp'}]}
```
