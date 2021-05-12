##
##
## Index for the pipe file descriptor in the queue array
QUEUE_FD=0

## Index of the pipe path in the queue array
QUEUE_PIPE_PATH=1


## Opens a named pipe for read and write and createss a global variable with the
## given name holding a structure representing the queue
## Receives the name of the queue as param
openQueue() {
  local queueName=$1
  local pipeName="/tmp/$queueName"

  # Create named pipe
  mkfifo $pipeName

  # Create the global variable for the queue and a local reference
  declare -ga $queueName
  local -n queue=$queueName
  queue=( 0 $pipeName )

  # Create file descriptor and redirect for read and write
  exec {queue[$QUEUE_FD]}<>${pipeName}

}

## Closes a queue by closing the file descriptor and deleting its pipe file.
## Receives the queue to close
closeQueue() {
  local -n queue=$1

  exec {queue[$QUEUE_FD]}<&-

  rm "${queue[$QUEUE_PIPE_PATH]}"

}

## Reads an item from a queue
## Receives the queue to read from
## Returns the item readed. It must be called using command substitution
## DATA=$(readQueue $MYQUEUE)
readQueue() {
  local -n queue=$1
  local data

  read -u ${queue[$QUEUE_FD]} data

  echo "$data"
}


## Writess an item to a queue
## Receives the queue to write to and a data item
writeQueue() {
  local -n queue=$1
  local fd=${queue[$QUEUE_FD]}

  echo "$2">&${fd}
}

## Helper function to get the type of a variable.
## Receives a variable.
## Returns a string with the type (str, int, array, map)
typeof() {

    local signature=$(declare -p "$1" 2>/dev/null)

    if [[ "$signature" =~ "declare --" ]]; then
        printf "str"
      elif [[ "$signature" =~ "declare -i" ]]; then
          printf "int"
    elif [[ "$signature" =~ "declare -a" ]]; then
        printf "array"
    elif [[ "$signature" =~ "declare -A" ]]; then
        printf "map"
    else
        printf "none"
    fi

}
