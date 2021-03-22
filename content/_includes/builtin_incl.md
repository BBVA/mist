# Builtin commands

`MIST` comes with a handful of builtin commands for the most basic tasks. This
set can be increased by the use of external repositories. Here follow the list
of builtin commands:


---
commandName: data
link: builtin_data.html
order: 1
---
<a id="data"></a>
## **data** command


### Description

This command define a knowledge base structure that can be populated later.
You can access to the component of the structure by using "." symbol
Every structure can store several instances.
They can be considered a stack and it can be iterated with the command "iterate".
When you have put more than one instances in a structure, you have direct access to the last instance inserted.


### Syntax

``` text
  data mydata {
    key1
    key2
    ...
  }
```


### Parameters

- myDaya: an identifier for the structure
- keyN: an identifier for a component inside the structure


### Examples

This example define the structure myHosys, put 3 instances and then print it.

``` text
  data myHosts {
    ip
    so
  }

  put "127.0.0.1" "linux" => myHosts
  put "windows" "192.168.1.23" => myHosts(so ip)
  put "8.8.8.8" "unknown" => myHosts

  # This print all the instaces inserted
  print myHosts

  # This print 8.8.8.8
  print myHosts.ip
```


---
commandName: put
link: builtin_put.html
order: 2
---
<a id="put"></a>
## **put** command


### Description

This command put data to the knowledge base.
The number of parameter must match with the data structure fields


### Syntax

``` text
  put IDorString [IDorString] [IDorString] ... => targetId
  put IDorString [IDorString] [IDorString] ... => targetId(field1 field2 field3...)
```


### Parameters

- IdorString: An string or an id with the name of the source local variable.
- targetId: data structure id of the knowledge base
- fieldX: optionally, you can chose the order of the fields to put


### Examples

``` text
  data myHosts {
    ip
    so
  }

  put "127.0.0.1" "linux" => myHosts
  put "windows" "192.168.1.23" => myHosts(so ip)
  put "8.8.8.8" "unknown" => myHosts

  data myIps {
    ip
  }

  iterate myHosts => host {
    put host.ip => MyIps
  }
```


---
commandName: print
link: builtin_print.html
order: 3
---
<a id="print"></a>
## **print** command


### Description

This command write an string, a local variable or a data structure of the knowledge base on console


### Syntax

``` text
  print IDorString
```


### Parameters

- IdorString: An string or an id with the name of the source local variable or data structure.


### Examples

``` text
  print "Program init"

  data myHosts {
    ip
    so
  }

  put "127.0.0.1" "linux" => myHosts
  put "192.168.1.23" "windows" => myHosts
  put "8.8.8.8" "unknown" => myHosts

  print myHosts

  iterate myHosts => host {
    print host.ip
  }
```


---
commandName: check
link: builtin_check.html
order: 4
---
<a id="check"></a>
## **check** command


### Description

This command check the value of a variable and execute commands if match.


### Syntax

``` text
  check id is value {
    ...
  }
```


### Parameters

- id: an identifier to match with value
- value: an identifier or string to match with id


### Examples

This example define the structure myHosys, put 1 instance, check the ip value and then print some log.

``` text
  data myHosts {
    ip
    so
  }

  put "127.0.0.1" "linux" => myHosts

  check myHosts.ip "127.0.0.1" {
    print "My IP is the same!"
  }
```


---
commandName: iterate
link: builtin_iterate.html
order: 5
---
<a id="iterate"></a>
## **iterate** command


### Description

This command iterate over a data list


### Syntax

``` text
  iterate myList => item {
    ...
  }
```


### Parameters

- myList: An id with the name of the source list: local variable or knowledge base id.
- item: the name of the local variable to map every item


### Examples

``` text
  data myHosts {
    ip
    so
  }

  put "127.0.0.1" "linux" => myHosts
  put "windows" "192.168.1.23" => myHosts(so ip)
  put "8.8.8.8" "unknown" => myHosts

  iterate myHosts => host {
    print host.ip
  }
```


---
commandName: exec
link: builtin_exec.html
order: 6
---
<a id="exec"></a>
## *exec* command


### Description


This command executes a custom user shell command


### Syntax

``` text
  exec myCustomCommand {
    input {
      param1 = param1value
      ...
    }
    output {
      result
      resultCode
      consoleOutput
      consoleError
    }
    then {
      ...
    }
  }
```


### Input parameters

- myCustomCommand: An string with the shell command I want to execute. You can parametrize it using {} place holders
- paramN: The value of the parameters used in the command


### Output parameters

- result: a string with values "Success" or "Error". Depending if the command could be executed successfully
- resultCode: the exit code provided after command execution
- consoleOutput: raw text with console standard output of the command.
- consoleError: raw text with console standard error of the command.


### Examples

List all files with "txt" extension

``` text
  exec "bash -c ls -1 {filter}" {
    input {
      filter = "*.txt"
    }
    output {
      result
      resultCode
      consoleOutput
      consoleError
    }
    then {
      print resultCode
    }
  }
```


---
commandName: searchInText
link: builtin_searchInText.html
order: 7
---
<a id="searchInText"></a>
## *searchInText* command


### Description

Search some regex in a text


### Syntax

``` text
  searchInText regex text {
    output {
      result
      found
    }
    then {
      ...
    }
  }
```


### Input parameters

- regex: a Python3 regex expression
- text: a variable that contains the text to look into.


### Output parameters

- result: a string with values "Success" or "Error". Depending if the command could be executed successfully
- found: "True" if regex was found. "False" otherwise


### Examples

Find a name in a phrase.

``` text
  data myData {
    text
  }
  put "Hello, my name is Peter and I like Mist!" => myData
  searchInText "Peter" myData.text {
    output {
      result
      found
    }
    then {
      check found is True {
        print "Peter found"
      }
    }
  }
```


---
commandName: searchInXML
link: builtin_searchInXML.html
order: 8
---
<a id="searchInXML"></a>
## *searchInXML* command


### Description

Search some xpath node in an XML string

Syntax
------

``` text
  searchInXML xpath text {
    output {
      result
      found
      value
    }
    then {
      ...
    }
  }
```


### Input parameters

- xpath: an XML xpath to search
- text: a variable that contains the XML text to look into.


### Output parameters

- result: a string with values "Success" or "Error". Depending if the command could be executed successfully
- found: "True" if xpath was found. "False" otherwise
- value: If found, it contains the value of the xpath node. "None" otherwise


### Examples

Find an item title in a xml document.

``` text
  data myData {
    XMLtext
  }

  put '''<?xml version="1.0" encoding="UTF-8"?>
  <bookstore>
    <book category="cooking">
      <title lang="en">Everyday Italian</title>
      <author>Giada De Laurentiis</author>
      <year>2005</year>
      <price>30.00</price>
    </book>
    <book category="children">
      <title lang="en">Harry Potter</title>
      <author>J K. Rowling</author>
      <year>2005</year>
      <price>29.99</price>
    </book>
  </bookstore>
  ''' => myData

  searchInXML "./book[2]/title" myData.XMLtext {
    output {
      r    esult
      found
      value
    }
    then {
      print result
      print found
      print value
    }
  }
```


---
commandName: searchInJSON
link: builtin_searchInJSON.html
order: 9
---
<a id="searchInJSON"></a>
## *searchInJSON* command


### Description

Search some jsonpath node in an JSON string


### Syntax

``` text
  searchInJSON jsonpath text {
    output {
      result
      found
      value
    }
    then {
      ...
    }
  }
```


### Input parameters

- jsonpath: a JSON path to search
- text: a variable that contains the JSON text to look into.


### Output parameters

- result: a string with values "Success" or "Error". Depending if the command could be executed successfully
- found: "True" if then jsonpath was found. "False" otherwise
- value: If found, it contains the value of the jsonpath node. "None" otherwise


### Examples

Find an item name in a json document.

``` text
  data myData {
    JSONtext
  }

  put '''
  {
  "employees": [
    {
      "id": 1,
      "name": "Pankaj",
      "salary": "10000"
    },
    {
      "name": "David",
      "salary": "5000",
      "id": 2
    }
  ]
  }
  ''' => myData

  searchInJSON "employees[1].name" myData.JSONtext {
    output {
      result
      found
      value
    }
    then {
      print result
      print found
      print value
    }
  }
```


---
commandName: csvDump
link: builtin_csvDump.html
order: 10
---
<a id="csvDump"></a>
## *CSVdump* command


### Description

This command write a data structure of the knowledge base into a CSV file


### Syntax

``` text
  CSVdump data => "targetFile.csv"
```


### Parameters

- data: An id with the name of the source data structure in the knowledge base
- "targetFile.csv": An string with the path and name of the target CSV file


### Examples

Define a data structure, fill it with some content, and dump it to a CSV file.

``` text
  data myHosts {
    ip
    so
  }

  put "127.0.0.1" "linux" => myHosts
  put "192.168.1.23" "windows" => myHosts
  put "8.8.8.8" "unknown" => myHosts

  CSVdump myHosts => "myHosts.csv"
```


---
commandName: csvPut
link: builtin_csvPut.html
order: 11
---
<a id="csvPut"></a>
## *CSVput* command


### Description

This command reads a CSV file and put all the data into the knowledge base


### Syntax

``` text
  CSVput "sourceFile.csv" => target
```


### Parameters

- "sourceFile.csv": An string with the path and name of the source CSV file
  (CSV header is mandatory, and delimiter must be a comma)
- target: An id with the target name in the knowledge base

Examples
--------

Read a csvFile

| IP           | SO       |
|:-------------|:---------|
| 127.0.0.1    | linux    |
| 192.168.1.23 | windows  |
| 8.8.8.8      | unknown  |

and iterate over it printing some of its content.

``` text
  CSVput "examples/nmap/myhosts.csv" => myHosts

  iterate myHosts => host {
    print host.ip
  }
```
