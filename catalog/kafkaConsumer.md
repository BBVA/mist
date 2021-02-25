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
