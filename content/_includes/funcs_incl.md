# Mist builtin functions


## AND

Boolean AND operator for the given values.

### Parameters
- values - List of values to apply the AND operation.

### Return value
Returns the resulting value of applying AND to all parameters.
    
## NOT

Boolean not operator.

### Parameters
- value

### Return value
Returns the negated value of `value`.
    
## OR

Boolean OR operator for the given values.

### Parameters
- values - List of values to apply the OR operation.

### Return value
Returns the resulting value of applying OR to all parameters.
    
## contains

Search `values` for `value` and returns true if it's contained.

### Parameters
- value - object to search for.
- values - Collection in which to look for.

### Return value
True if `values` contains `value`, false otherwise.
    
## abort

Abort mist script execution. The program will end inmediatelly and no registered finally hook will be executed.

### Parameters
- reason - A text describing the cause.
    
## print

Print the arguments in a standard output line.

### Parameters
- texts - Variable list of arguments to print.
    
## dict2list

Convert a dictionary into a list.

### Parameters
- l - source dictionary.
- names - list of key to include into the resulting list.

### Return and sent value
The resulting list.
    
## exec

Runs the given command and returns its output.

### Parameters
- command - Command line text to execute.
- printOutput - Print standard output to the MIST standard output, defaults to true.
- interactive - Runs the command in interactive mode, defaults to false.

### Return value
Returns a dictionary containing the command stderr and stdout and the exit code and description.
    
## writeLine

Writes a line of text in the given file.

### Parameters
- name - Path of the file to write to.
- line - String with the content of the line to write in the file.
    
## filterDict

Returns a dictionary containing only the selected entries. If `newNames` is provided the keys are replaced.

### Parameters
- d - Source dictionary.
- names - List of keys to filter.
- newNames - Replacement values for the filtered keys

### Return and send value
The filtered dictionary.
    
## get

Return the element of the list at the given index.

### Parameters
- l - List containing elements.
- index - The requested index.

### Return value
Returns the element at the given index.
    
## if

Execute the enclosed commands if `val` is true.

### Parameters
- right - Boolean expression.

### Return value
Returns true if `val` is true, false otherwise.
    
## isEqual

Compares two operands and execute the enclosed commands if both are equal.

### Parameters
- left - Operand to compare.
- right - Operand to compare.

### Return value
Returns true if both operands are equal, false otherwise.
    
## isGreater

Compares two operands and execute the enclosed commands if `left` is greater than `right`.

### Parameters
- left - Operand to compare.
- right - Operand to compare.

### Return value
Returns true if `left` is greater than `right`, false otherwise.
    
## iterate

Iterates over the elements of a collection while executing the enclosed commands.

### Parameters
- items - Collection.
- name - desc.
    
## kill

Kill the current process.
    
## list2dict

Convert a list into a dictionary.

### Parameters
- l - source list.
- names - list of names for the resulting dictionary.

### Return and sent value
The resulting dictionary.
    
## map

Replace the elements of the given list by aplying the map function to each of them.

### Parameters
- l - List to process.
- mapFunc - The function to apply to the list elements, must be defined as mapFunc(val) => val.

### Return value
Returns the list modified.
    
## reduce

Returns the value produced by reduceFunc after applyng it to all the elements of the given list.

### Parameters
- l - List to process.
- reduceFunc - The function to process the list elements, must be defined as reduceFunc(base, val) => val.

### Return value
Returns the value produced.
    
## len

Returns the length of the given object.

### Parameters
- l - Object.

### Return value
Returns the length.
    
None
## parseInt

Transforms the string value to integer if possible.

### Parameters
- value - String value.

### Return value
Integer representation of `value`.
    
## parseJSON

Loads a JSON document from a string.

### Parameters
- jsonstr -  String containing the JSON document.

### Return value
Returns a JSON document.
    
## processWriteLine

Writes a line of text to a process standard input.

### Parameters
- p - Process descriptor.
- input - Text to write.
    
## eval

Evaluates the given Python expressions.

### Parameters
- command - Python expression to evaluate.

### Return value
Retuens the result of evaluating the given expression.
    
## range

Creates a list with values generated in the range defined by the parameters.

### Parameters
- begin - First value in the range.
- end - Last value, not included, in the range.
- step - Increment used to generate values, defaults to 1 if begin < end, -11 if end < begin.

### Return value
A list with all the values generated.
    
## readFile

Reads the full content from a given file.

### Parameters
- path - File path.

### Return value
Returns the file content.
    
## readFileAsLines

Reads the full content from a given file as text lines.

### Parameters
- path - File path.

### Return value
Returns a list with all the lines readed from the file.
    
## readJSON

Reads a JSON document from a file.

### Parameters
- jsonfilepath - Path to the file containing the JSON document.

### Return value
Returns a JSON document.
    
## registerFinallyHook

Register a function to be executed at the end of the program

### Parameters
- fname - string with the name of the function
- *p - parameters for the function
    
## searchInJSON

Finds all the matches of the `JSONpath` expresion in a JSON document.

### Parameters
- jsonpath - JSONpath expression to define the search.
- text - The JSON document to search in.

### Return value
A list with all the matches found.
    
## searchInText

Finds all the matches of the `regex` expresion in text.

### Parameters
- regex - Regular expression to define the search.
- text - The text to search in.

### Return value
A list with all the matches found.
    
## searchInXML

Finds all the matches of the `xpath` expresion in a XML document.

### Parameters
- xpath - Xpath expression to define the search.
- text - The XML document to search in.

### Return value
A list with all the matches found.
    
## sleep

Sleep the current process during the given amount of time.

### Parameters
- seconds - Seconds to sleep, if given this value takes precedence.
- ms - Millieconds to sleep, if no secons parameter is given this value is used.
    
## strSubstr

Returns a substring.

### Parameters
- s - String.
- start - Start position.
- end - end position.

### Return value
Returns a substring.
    
## terminate

Description.

### Parameters
- name - desc.
- name - desc.
    
## tmpFile

Creates a temporary file and returns its path.

### Parameters
- delete - Boolean, defaults to false. The file is deleted after closing it.

### Return value
Returns the new temporary file's path.
    
## toString

Converts the argument to string.

### Parameters
- value - The value to convert to string.

### Return value
`value` converted to string.
    
## uuidStr

Generates and returns a UUID version 4.

### Return value
The generated UUID.


## Utility functions

Mist, in addition to all the previous functions, provides developers with some
utility functions to handle with strings, dictionaries and lists that are
imported directly from Python.

You can see the documentation about all these funcions in [Python's documentation](https://docs.python.org/3/library/stdtypes.html)

### String utility functions

The following functions are available: [capitalize](https://docs.python.org/3/library/stdtypes.html#str.capitalize), [casefold](https://docs.python.org/3/library/stdtypes.html#str.casefold), [center](https://docs.python.org/3/library/stdtypes.html#str.center), [count](https://docs.python.org/3/library/stdtypes.html#str.count), [encode](https://docs.python.org/3/library/stdtypes.html#str.encode), [endswith](https://docs.python.org/3/library/stdtypes.html#str.endswith), [expandtabs](https://docs.python.org/3/library/stdtypes.html#str.expandtabs), [find](https://docs.python.org/3/library/stdtypes.html#str.find), [format](https://docs.python.org/3/library/stdtypes.html#str.format), [format_map](https://docs.python.org/3/library/stdtypes.html#str.format_map), [index](https://docs.python.org/3/library/stdtypes.html#str.index), [isalnum](https://docs.python.org/3/library/stdtypes.html#str.isalnum), [isalpha](https://docs.python.org/3/library/stdtypes.html#str.isalpha), [isascii](https://docs.python.org/3/library/stdtypes.html#str.isascii), [isdecimal](https://docs.python.org/3/library/stdtypes.html#str.isdecimal), [isdigit](https://docs.python.org/3/library/stdtypes.html#str.isdigit), [isidentifier](https://docs.python.org/3/library/stdtypes.html#str.isidentifier), [islower](https://docs.python.org/3/library/stdtypes.html#str.islower), [isnumeric](https://docs.python.org/3/library/stdtypes.html#str.isnumeric), [isprintable](https://docs.python.org/3/library/stdtypes.html#str.isprintable), [isspace](https://docs.python.org/3/library/stdtypes.html#str.isspace), [istitle](https://docs.python.org/3/library/stdtypes.html#str.istitle), [isupper](https://docs.python.org/3/library/stdtypes.html#str.isupper), [join](https://docs.python.org/3/library/stdtypes.html#str.join), [ljust](https://docs.python.org/3/library/stdtypes.html#str.ljust), [lower](https://docs.python.org/3/library/stdtypes.html#str.lower), [lstrip](https://docs.python.org/3/library/stdtypes.html#str.lstrip), [maketrans](https://docs.python.org/3/library/stdtypes.html#str.maketrans), [partition](https://docs.python.org/3/library/stdtypes.html#str.partition), [replace](https://docs.python.org/3/library/stdtypes.html#str.replace), [rfind](https://docs.python.org/3/library/stdtypes.html#str.rfind), [rindex](https://docs.python.org/3/library/stdtypes.html#str.rindex), [rjust](https://docs.python.org/3/library/stdtypes.html#str.rjust), [rpartition](https://docs.python.org/3/library/stdtypes.html#str.rpartition), [rsplit](https://docs.python.org/3/library/stdtypes.html#str.rsplit), [rstrip](https://docs.python.org/3/library/stdtypes.html#str.rstrip), [split](https://docs.python.org/3/library/stdtypes.html#str.split), [splitlines](https://docs.python.org/3/library/stdtypes.html#str.splitlines), [startswith](https://docs.python.org/3/library/stdtypes.html#str.startswith), [strip](https://docs.python.org/3/library/stdtypes.html#str.strip), [swapcase](https://docs.python.org/3/library/stdtypes.html#str.swapcase), [title](https://docs.python.org/3/library/stdtypes.html#str.title), [translate](https://docs.python.org/3/library/stdtypes.html#str.translate), [upper](https://docs.python.org/3/library/stdtypes.html#str.upper), [zfill](https://docs.python.org/3/library/stdtypes.html#str.zfill).

### Dictionary utility functions

The following functions are available: [clear](https://docs.python.org/3/library/stdtypes.html#str.clear), [copy](https://docs.python.org/3/library/stdtypes.html#str.copy), [fromkeys](https://docs.python.org/3/library/stdtypes.html#str.fromkeys), [get](https://docs.python.org/3/library/stdtypes.html#str.get), [items](https://docs.python.org/3/library/stdtypes.html#str.items), [keys](https://docs.python.org/3/library/stdtypes.html#str.keys), [pop](https://docs.python.org/3/library/stdtypes.html#str.pop), [popitem](https://docs.python.org/3/library/stdtypes.html#str.popitem), [setdefault](https://docs.python.org/3/library/stdtypes.html#str.setdefault), [update](https://docs.python.org/3/library/stdtypes.html#str.update), [values](https://docs.python.org/3/library/stdtypes.html#str.values).

### List utility functions

The following functions are available: [append](https://docs.python.org/3/library/stdtypes.html#str.append), [clear](https://docs.python.org/3/library/stdtypes.html#str.clear), [copy](https://docs.python.org/3/library/stdtypes.html#str.copy), [count](https://docs.python.org/3/library/stdtypes.html#str.count), [extend](https://docs.python.org/3/library/stdtypes.html#str.extend), [index](https://docs.python.org/3/library/stdtypes.html#str.index), [insert](https://docs.python.org/3/library/stdtypes.html#str.insert), [pop](https://docs.python.org/3/library/stdtypes.html#str.pop), [remove](https://docs.python.org/3/library/stdtypes.html#str.remove), [reverse](https://docs.python.org/3/library/stdtypes.html#str.reverse), [sort](https://docs.python.org/3/library/stdtypes.html#str.sort).


