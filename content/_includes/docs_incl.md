<a id="Introduction"></a>

# Mist Documentation

<a id="Documentation"></a>

When you need to create complex Workflows and need to communicate different tools working together, maybe you need `MIST`.

# What is MIST

`MIST` is a high level programming language for defining executions workflows easily.

`MIST` is interpreted. So, you can use their command line interpreter for running `.mist` programs. `MIST` interpreter will create the workflow graph, execute each tool, manage executions and synchronization fo you.

A quick example about how to run a `MIST` program:

```bash
> mist run my_program.mist
```

# Installing

```bash
> pip install mist-lang
```



<a id="QuickStart"></a>
# Quick Start

## Requirements

Before start, we should install some command line tools used by catalog functions in the Demos:

### dnsrecon (for searchDomains)

- Mac & Linux: `pip install git+https://github.com/cr0hn/dnsrecon`

### nmap (fir findOpenPorts)

- Mac: `brew install nmap`
- Ubuntu: `sudo apt install nmap`

### kafka-console-consumer & kafka-console-producer

- Mac: `brew install kafka`
- Ubuntu: `sudo apt install kafka`

NOTE: For Demo 3 to 5 a Kafka server is expected to be running at localhost

### festin

- Mac & Linux: `pip install festin`

NOTE: Is also recommended to install **tor** in order to prevent being banned when using festin

## aws (for S3Store)

- Mac: `brew install awscli`
- Ubuntu: `sudo apt install awscli`

## Demo 1 - The simplest scenario

**Explanation**

In this scenario we'll do:

1. `CLI Input` - Read a domain as a parameter from CLI.
2. `Search Domains` - Use MIST function for search related domains / sub-domains from a start domain.
3. `Fin OpenPorts` - Search open port for each new domain / sub-domain found.   
4. `Screen (Pring)` - Displays the results into the screen (by using MIST 'print' function).

**Use case diagram**

![Demo 1](content/assets/images/mist-demo-1.png)

**MIST code** (examples/demo/scenario-01.mist)

```bash
include "searchDomains" "findOpenPorts"

searchDomains(%domain) => findOpenPorts("80,443") => print()
```

**Execute**

```bash
> mist run examples/demo/scenario-01.mist domain=example.com
```

## Demo 2 - Sending results to Kafka

**Explanation**

In this scenario we'll do:

1. `CLI Input` - Read a domain as a parameter from CLI.
2. `Search Domains` - Use MIST function for search related domains / sub-domains from a start domain.
3. `FindOpenPorts` - Search open port for each new domain / sub-domain found.   
4. `Kafka output` - Send results to a Kafka topic.

**Use case diagram**

![Demo 2](content/assets/images/mist-demo-2.png)

**MIST code** (examples/demo/scenario-02.mist)

```bash
include "searchDomains" "findOpenPorts" "kafkaProducer"

searchDomains(%domain) => findOpenPorts("80,443") =>
    kafkaProducer($KAFKA_SERVER, "domainsTopic")
```

**Execute**

```bash
> mist run examples/demo/scenario-02.mist domain=example.com
```

## Demo 3 - Adding new tool and remove duplicate domains

**Explanation**

In this scenario we'll do:

1. `CLI Input` - Read a domain as a parameter from CLI.
2. Search domains:
    1. `Search Domains` - Use MIST function for search related domains / sub-domains from a start domain.
    2. `Festin` - Use MIST integration for [Festin](https://github.com/cr0hn/festin) for search related domains / sub-domains from a start domain.
3. `Filter Repeated` - Use MIST function to detect and remove repeated found domains.   
4. `Fin OpenPorts` - Search open port for each new domain / sub-domain get from `Fitler Repeated`.   
5. `Kafka output` - Send results to a Kafka topic.  

**Use case diagram**

![Demo 3](content/assets/images/mist-demo-3.png)

**MIST code** (examples/demo/scenario-03.mist)

```bash
include "searchDomains" "festin" "findOpenPorts" "filterRepeated" "kafkaProducer"

searchDomains(%domain) => foundDomains
festin(%domain, $DNS_SERVER, True) => foundDomains

foundDomains => filterRepeated(False) =>
    findOpenPorts("80,443") => kafkaProducer($KAFKA_SERVER, "domainsTopic")
```

**Execute**

```bash
> mist run examples/demo/scenario-03.mist domain=example.com
```

## Demo 4 - Send results to Kafka and S3 through a dispatcher

**Explanation**

In this scenario we'll do:

1. `CLI Input` - Read a domain as a parameter from CLI.
2. Search domains:
    1. `Search Domains` - Use MIST function for search related domains / sub-domains from a start domain.
    2. `Festin` - Use MIST integration for [Festin](https://github.com/cr0hn/festin) for search related domains / sub-domains from a start domain.
3. `Filter Repeated` - Use MIST function to detect and remove repeated found domains.   
4. `Find OpenPorts` - Search open port for each new domain / sub-domain get from `Fitler Repeated`.   
5. `Dispatcher (80 / 443)` - Split results and send each port to a different queue.
6. Send results:
    1. `Kafka output` - Send found 80 ports to a Kafka topic.   
    2. `S3 output` - Send found 443 ports to a AWS S3 bucket.   

**Use case diagram**

![Demo 4](content/assets/images/mist-demo-4.png)

**MIST code** (examples/demo/scenario-04.mist)

```bash
include "searchDomains" "festin" "findOpenPorts" "filterRepeated" "kafkaProducer" "S3Store"

function dispatcher(p) => kafka, S3 {
    if (isEqual(p.port, "80")) {
        p => kafka
    } else {
        p => S3
    }
}

searchDomains(%domain) => foundDomains
festin(%domain, $DNS_SERVER, True) => foundDomains

foundDomains => filterRepeated(False) =>
    findOpenPorts("80,443") => dispatcher() => kafkaOutput, S3Output

kafkaOutput => kafkaProducer($KAFKA_SERVER, "domainsTopic")
S3Output => S3Store($BUCKET_URI)
```

**Execute**

```bash
> mist run examples/demo/scenario-04.mist domain=example.com
```

## Demo 5 - Read from Kafka and a File

**Explanation**

In this scenario we'll do:

1 Input from multiple sources:
   1. `File Input` - Read domains from an external file.
   2. `Kafka Input` - Read domains from Kafka topics.
   3. `CLI Input` - Read domains from CLI.
2. Search domains:
    1. `Search Domains` - Use MIST function for search related domains / sub-domains from a start domain.
    2. `Festin` - Use MIST integration for [Festin](https://github.com/cr0hn/festin) for search related domains / sub-domains from a start domain.
3. `Filter Repeated` - Use MIST function to detect and remove repeated found domains.   
4. `Find OpenPorts` - Search open port for each new domain / sub-domain get from `Fitler Repeated`.   
5. `Dispatcher (80 / 443)` - Split results and send each port to a different queue.
6. Send results:
    1. `Kafka output` - Send found 80 ports to a Kafka topic.   
    2. `S3 output` - Send found 443 ports to a AWS S3 bucket.

**Use case diagram**

![Demo 5](content/assets/images/mist-demo-5.png)

**MIST code** (examples/demo/scenario-05.mist)

```bash
include "searchDomains" "festin" "findOpenPorts" "filterRepeated" "kafkaProducer" "S3Store" "kafkaConsumer" "tail"

function dispatcher(p) => kafka, S3 {
    if (isEqual(p.port, "80")) {
        p => kafka
    } else {
        p => S3
    }
}

kafkaConsumer($KAFKA_SERVER, "inputTopic", "*END*", False) => inputDomains
tail("domains.txt", "*END*") => inputDomains
%domain => inputDomains

inputDomains => searchDomains() => foundDomains
inputDomains => festin($DNS_SERVER, True) => foundDomains

foundDomains => filterRepeated(False) => findOpenPorts("80,443") =>
    dispatcher() => kafkaOutput, S3Output

kafkaOutput => kafkaProducer($KAFKA_SERVER, "domainsTopic")
S3Output => S3Store($BUCKET_URI)
```

**Execute**

```bash
> mist run examples/demo/scenario-05.mist domain=example.com
```




## Authors

MIST is being developed by BBVA-Labs Security team members.

## Contributions

Contributions are of course welcome. See [CONTRIBUTING](https://github.com/BBVA/mist/blob/master/CONSTRIBUTING.md) or skim existing tickets to see where you could help out.

## License

MIST is Open Source Software and available under the [Apache 2 license](https://github.com/BBVA/mist/blob/master/LICENSE)
