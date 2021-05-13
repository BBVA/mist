# *mongoWatch* command

## Description

Subscribe to a MongoDB collection for new inserts.
Every time that a document is inserted in the collection it will be send for the output stream
This command run for ever. If you want to stop the program you will need to do Control-C
or programatically call to abort function

*NOTE*: Due to MongoDB limitations the database must be a replicaset. An stand alone database will not work.

## Concurrency Type

Async

## Input parameters

- **uri**: MongoDB URI including database. i.e.: mongodb+srv://cluster0.ou8h3.mongodb.net/myDatabase
- **user**: Username for MondoDB connection
- **password**: Password for MondoDB connection
- **collection**: Collection to watch for new inserts.

## Output parameters

The document inserted. Output stream.

## Tools and services

The following commands need to be available in your command path:

- mongo

## Example

Use $MONGO... enrivonment variables to connect to MongoDB.  
Watch "customers" collection.  
Print every new document inserted.  

```bash
include "mongoWatch"

mongoWatch($MONGO_URI, $MONGO_USER, $MONGO_PASSWORD, "customers") => doc

doc => print()
```
