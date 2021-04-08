# MIST core syntax

This file explain the basic syntax and features of MIST Language.

## Comments

Any line starting with # is a comment

## Data types and asignations

In MIST there are 3 basic data types: booleans, integers and strings.
In addition, exists complex data structures: Dictionaries and List.
The asignation operator is "="

### Booleans

Mist have suport for booleans: True and False
You can use NOT and AND function to create complex boolean expressions.

```bash
foo = True
bar = False

foobar = AND(NOT(foo, NOT(bar))
```

### Integers

Mist have support for integers numbers. For now, there are no arithmetic operators but it will be in the future.

foo = 43

### Strings

Like other languages, strings are delimited by "

```bash
foo = "John"
```

In adition, you can use {} tu create formatted strings that include values from variables or function calls.

```bash
bar = "Hi {foo}"
```

### Dictionaries

Dictionaries are difined with JSON syntax and you can access it with []. It can contain values of different types.

```bash
mydict = { "foo": 4, "bar": "John"}
foo = mydict["foo"]
```

### Lists

Lists are difined with JSON syntax and you can access it with [index]. It can contain values of different types.

```bash
mylist = ["foo", "bar"]
foo = mylist[0]
```

## Variables and Parameters

Use de operator $ to access environments variables.

```bash
print($PATH)
```

Use de operator % to access to command line parameters.

```bash example.mist
print(%p1)
```

```bash
>mist run example.mist p1=hello
hello
```

## Conditionals

The syntax of conditional expressions is:

if (boolean expresion) {
    commands...
} elsif (boolean expresion) {
    commands...
} else {
    commands...
}

See the following example:

```bash
foo = False
bar = True

if (foo) {
  print("A")
} elsif (bar) {
  print("B")
} else {
  print("C")
}
```

The result of the code is "B"

## Functions

MIST follow an structured paradign similar to C Language. So the basic structure item is the function.

You can define a function with the following syntax:

```bash
function functionName (param1name, param2name, ...) [=> out1, out2...] {
    commands...
    return value
}
```

NOTE: Be aware that out1 and out2 is refered to pipes and not to the return value. This will be explained in the Pipes section.

Example:

```bash
function salute(name) {
    return "Hello {name}"
}

You can invoke a function with positional parameters or with named parameters. For example, invoking previous defined function:

```bash
print(salute("John"))
print(salute(name="John"))
```

## Variable Scopes

Variables defined outside a function can be considered global variables because they are visible inside other funcion as long as there are no other variable defined with the same name inside the function.

Variables defined inside a funcion are only visibles inside the function.

```bash
global = "Global"

function test() {
  local = "Local"
  # global exists here
  # local exists here
}

# global exists here
# local NOT exists here

function test2(global) {
  # global exists here but is not the same. It is a local variable with the same name that hide the real global
}
```

## Include and Import

For organizing the code. Mist provides the directives *include* and *import*

### Include files

*include* is used to include .mist files in your code. The result is exactly like copy the content of the specified file in your own file. Example:

```bash
include "./lib/module.mist"
include "module.mist"
include "https://github.com/BBVA/mist/raw/master/mist/catalog/festin.mist"
```

The first line include the local file module.mist at lib directory
The second line include module.mist from current directory or from local catalog directory.
The third line include the remote file festin.mist

### Import files

MIST is implemented in Python. And you can import Python functions and work with them in MIST. *import* directive imports all the funcions defined in a Python file. Example:

```python file=./test/mist_files/mylib.py
def myPrint(s: str, stack:list=None, commands:list=None):
    print(">",s)
```

```bash file=myProgram.mist
import "./test/mist_files/mylib.py"
mylibMyPrint("Hola")
```

Note that Python functions receives 2 additional parameters: *stack* and *commands*. You can use those parameters to implement advanced functionality.
The *import* directive can also import remote files. Example:

```bash file=myProgram.mist
import "https://raw.githubusercontent.com/BBVA/mist/master/test/mist_files/mylib.py"
mylibMyPrint("Hola")
```

## Streams

## Finally Hook

## Structures and Watch?????

## Abort vs done?
