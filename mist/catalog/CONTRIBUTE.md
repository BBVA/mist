# CONTRIBUTE to MIST catalog

There several ways to contribute to MIST:

- Contribute to MIST catalog (this document)
- Contribute to MIST built-in functions
- Contribute to MIST core

In this document we are going to see how to create and include new catalog commands to MIST.

The catalog is what really turn MIST into a powerfull language for your script flows.

Here you can find lots of tools that you can easily include in your flows inmediatelly.

Of course, you can invoke another tools by using exec command, but it is better to create a catalog entry for the tool so any other user can reuse it in the future.

## Before start

Before starting to work in your command, review if the tool that you whant to use is already included in the MIST catalog or exists as a built-in function of MIST.

Then, locate the requirement of the command. Most of the times, you want to include a command line tool and it should be installed and available in your system PATH.

Now, we are going to see an example step by step.

## Files that you must include

Every catalog entry has two files:

- "myCommand.mist": that include a header and the mist code of the command.
- "myCommand.md": that include the documentation and example of the command.

### Mist code requirements

The .mist file must include a header like this:

```bash
# Name: findOpenPorts
# Version: 2.0.0
# Concurrency: Sync and Async
# Description: Find open ports at some specific host
# Tags: ports, network, nmap
```

And then, the function. In this case "findOpenPorts".

Of course, you can have more functions depending on your needs.

### Implementing a syncronous command (nmap)

Now, lets see a syncronous implementation of nmap command. Pay attention to the inline comments.

```bash
function findOpenPorts(ip, ports) {
    openPorts = [] # In this variable we will store the open ports found
    # we call exec command to execute nmap with the given parameter.
    r = exec("nmap -p {ports} --open {ip}", False) {
        # this block of code is executed for every line of the nmap output (outputLine)
        fields = strSplit(outputLine) # split the line by spaces or tabs
        isGreater(len(fields),1) { # if the line has more than 1 field
            isEqual(get(fields,1), "open") { # if the field 1 is "open"
                openPort = strSplit(get(fields,0),"/") # get the field 0 and remove "/tcp" or "/udp"
                listAppend(openPorts, {"port": openPort[0], "protocol": openPort[1]}) # append the port found to "openPorts"
            }
        }
    }
    # r contains the result of the execution: result, resultCode, consoleOutput, consoleError
    # Now we add "openPorts" to r
    r["openPorts"] = openPorts 
    return r
}
```

That is it. The function is ready to use syncronously it like this:

```bash
include "findOpenPorts"
r = findOpenPorts("127.0.0.1", "0-9000")
print(r)
```

### Implementing an asyncronous command (nmap)

We are going to convert the previous syncronous implementation in a both sync and async implementation.

```bash
function findOpenPorts(ip, ports) {
    openPorts = []
    r = exec("nmap -p {ports} --open {ip}", False)  => out { # we add the output stream
        fields = strSplit(outputLine)
        isGreater(len(fields),1) {
            isEqual(get(fields,1), "open") {
                openPort = strSplit(get(fields,0),"/")
                listAppend(openPorts, {"port": openPort[0], "protocol": openPort[1]})
                # The following lines send the message to out stream
                message = {"ip": ip, "port": openPort[0], "protocol": openPort[1]}
                message => out
            }
        }
    }
    r["openPorts"] = openPorts 
    return r
}
```

Now, we can also use the command asyncronouly with streams. For example:

```bash
include "findOpenPorts"
"127.0.0.1" => findOpenPorts("0-9000") => print()
```

### Command documentation

With your command implementacion it is mandatory to include a proper .md documentation file with at least the following sections:

- Description
- Concurrency Type (Sync, Async, or Both)
- Input parameters
- Output parameters
- Tools and services
- Examples

## Creating your own catalog

As long as MIST is able to import MIST files locally and remotelly, you can create your own MIST catalog.

See the section "Include files" of SYNTAX.md to get more information about this.

## Pull request to MIST catalog

Finally, you can do a pull request with the 2 files of your command (.mist and .md) to MIST github repository.

We will be very glad for your apportation and you probably help to other MIST users.
