# Mist Catalog


<a id="mist/catalog/S3Store.md"></a>
# *S3Store* command

## Description

This command stores the data received as lines in the given S3 URI. This command
is intended to be used with a stream.

## Input parameters

- **text**: Source stream to read text lines from
- **remoteUri**: S3Uri of the remote object to create. Must contain bucket, prefix
and object name

## Output parameters

None.

## Dependencies

This command requires the AWS CLI and the credentials configuration in place.

## Examples

Store the data received from the stream *:source* as s3://myBucket/facts/list.txt.

``` text
S3Store(:source, "s3://myBucket/facts/list.txt")
```

## Auxiliar functions

### *S3Writer*

This function copies a local file in the given S3Uri.

### Input parameters

- **localPath**: Path of the local file to copy
- **remoteUri**: S3Uri of the remote object to create


<a id="mist/catalog/festin.md"></a>
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


<a id="mist/catalog/filterRepeated.md"></a>
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


<a id="mist/catalog/findOpenPorts.md"></a>
# *findOpenPorts* command

## Description

This command performs a port scan to a target host.

## Concurrency Type

Sync or Async

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

NOTE: when used with a queue the list of openPorts will be send with the format: {"ip": "1.2.3.4", "port": 443, "protocol": "tcp"}

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


<a id="mist/catalog/gitLeaksFinder.md"></a>
# *gitLeaksFinder* command

## Description

Finds sensitive information in Git repositories.

## Concurrency Type

Sync

## Input parameters

- **gitPath**: Path of Git repositories.

## Output parameters

- **result**: Boolean, possible values are: True, if the gitleaks command has been
executed without errors and not issues detected, or False otherwise.
- **resultCode**: Integer. Exit code from gitleaks command.
- **consoleOutput**: Raw text with console output from gitleaks command.
- **consoleError**: Raw text with console error from gitleaks command.
- **issues**: List of issues found by analyzer.

Issues contains an array of objects with the following information:

``` json
  [
    {
      "commit": {COMMIT-ID},
      "repo": {REPO NAME},
      "rule": {RULE NAME},
      "line": {LINE NUMBER}
    }
  ]
```

## Tools and services

The following commands need to be available in your command path:

- gitleaks

## Examples

Find sensitive information in git repository at current directory

``` text
include "gitLeaksFinder"
r = gitLeaksFinder("./")
print(r)
```

Example output:

```text
{'result': False, 'resultCode': 1, 'consoleOutput': '\x1b[36mINFO\x1b[0m[2021-02-17T16:46:02+01:00] report written to /var/folders/vt/0gyg50fx3_q3nn0dwhmjgynh0000gp/T/tmpuwfs8mvr\n\x1b[33mWARN\x1b[0m[2021-02-17T16:46:02+01:00] 1 leaks detected. 9 commits scanned in 1 second 738 milliseconds 202 microseconds', 'consoleError': '', 'issues': [{'line': '          "current_key": "XXXXXXXXXXXXXXXXXXX"', 'lineNumber': 24, 'offender': 'XXXXXXXXXXXXXXXXXXX', 'commit': 'XXXXXXXXXXXXXXXXXXX', 'repo': 'XXXXXXXXXXXXXXXXXXX', 'rule': 'Google API key', 'commitMessage': 'Version 1.0.2\n', 'author': 'XXXXXXXXXXXXXXXXXXX', 'email': 'XXXXXXXXXXXXXXXXXXX', 'file': 'google-services.json', 'date': '2019-08-25T14:14:34+02:00', 'tags': 'key, Google', 'operation': 'addition'}]}
```


<a id="mist/catalog/kafkaConsumer.md"></a>
# *kafkaConsumer* command

## Description

Read from a Kafka topic and send values to a queue.

## Concurrency Type

Async. This function have to be alwais used with a target queue.

## Input parameters

- **servers**: String. Server list for bootstrap-server options. Example: "127.0.0.1:9092"
- **topic**: String. Kafka topic to listen.
- **endMessage**: String. When this message arrives the consumer will terminate.
- **fromBeginning**: Boolean. True for read the topic from the beginning.

## Output parameters

Every message received in the topic will be send to the queue.

## Tools and services

The following commands need to be available in your command path:

- kafka-console-consumer

## Examples

Connect to Kafka at 127.0.0.1:9092, listen the topic "myTopic" for new messages and send then to "myQueue".
When the message "END" arrives, stop listening and finish the process.

``` text
include "kafkaConsumer"

function echo(s) {
    print(s)
}

kafkaConsumer("127.0.0.1:9092", "prueba", "END", True) => myQueue
echo(:myQueue)
```


<a id="mist/catalog/kafkaProducer.md"></a>
# *kafkaProducer* command

## Description

Write messages to a Kafka topic

## Concurrency Type

Sync(for one message) or Async(for muliple messages received in a queue)

## Input parameters

- **message**: String. The message to send. You may also want to use a source queue here.
- **servers**: String. Server list for bootstrap-server options. Example: "127.0.0.1:9092"
- **topic**: String. Kafka topic to send messages.

## Output parameters

Every "message" received will be send to kafka topic.

## Tools and services

The following commands need to be available in your command path:

- kafka-console-producer

## Examples

Async. Connect to Kafka at 127.0.0.1:9092, listen the topic "q" for new messages and send then to Kafla topic "prueba".

``` text
include "kafkaProducer"

kafkaProducer(:q, "127.0.0.1:9092", "prueba")

send("msg1","q")
send("msg2","q")
```

Sync. Connect to Kafka at 127.0.0.1:9092 and send the message "hello" to Kafla topic "prueba".

``` text
include "kafkaProducer"

kafkaProducer("hello", "127.0.0.1:9092", "prueba")
```


<a id="mist/catalog/pythonCodeAnalysis.md"></a>
# *PythonCodeAnalysis* command

## Description

Performs security code analysis on Python code.

## Concurrency Type

Sync

## Input parameters

- **sources**: Path of Python source code.

## Output parameters

- **result**: Boolean, possible values are: True, if the gitleaks command has been
executed without errors and not issues detected, or False otherwise.
- **resultCode**: Integer. Exit code from gitleaks command.
- **consoleOutput**: Raw text with console output from gitleaks command.
- **consoleError**: Raw text with console error from gitleaks command.
- **issues**: List of issues found by the analyzer.

## Tools and services

The following commands need to be available in your command path:

- bandit

## Examples

**Basic**: Find vulnerabilities in python code ay current directory

``` text
include "gitLeaksFinder"
r = gitLeaksFinder("./")
print(r)
```


<a id="mist/catalog/searchDomains.md"></a>
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

- dnsrecon

## Example

Find related domains for "bbva.com" and print result

``` text
include "searchDomains"
r = searchDomains("bbva.com")
print(r)
```


<a id="mist/catalog/tail.md"></a>
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
