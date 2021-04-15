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

Abort mist script execurion.

### Parameters
- reason - A text describing the cause.
    
## print

Print the arguments in a standard output line.

### Parameters
- texts - Variable list of arguments to print.
    
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

### Return value
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

