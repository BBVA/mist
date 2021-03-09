# *kafkaProducer* command

## Description

Write messages to a Kafka topic

## Concurrency Type

Sync(for one message) or Async(for muliple messages received in a queue)

## Input parameters

- **servers**: String. Server list for bootstrap-server options. Example: "127.0.0.1:9092"
- **topic**: String. Kafka topic to send messages.
- **message**: String. The message to send. You may also want to use a source queue here.

## Output parameters

Every "message" received will be send to kafka topic.

## Tools and services

The following commands need to be available in your command path:

- kafka-console-producer

## Examples

Async. Connect to Kafka at 127.0.0.1:9092, listen the topic "q" for new messages and send then to Kafla topic "prueba".

``` text
include "kafkaProducer"

kafkaProducer("127.0.0.1:9092", "prueba", :q)

send("msg1","q")
send("msg2","q")
```

Sync. Connect to Kafka at 127.0.0.1:9092 and send the message "hello" to Kafla topic "prueba".

``` text
include "kafkaProducer"

kafkaProducer("127.0.0.1:9092", "prueba", "hello")
```
