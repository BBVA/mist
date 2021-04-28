##
##
## Starting file descriptor for queus
QUEUE_MIN=100

## Index of the file descriptor for reads
QUEUE_READ_FD=0

## Index of the file descriptor for writes
QUEUE_WRITE_FD=1

## Index of the pipe path
QUEUE_PIPE_PATH=2


## Opens a queue for read and write and returns an structure with their file descriptors
## Receives the name of the queue as param
## Returns an array with the input and output file descriptors. It must be called using evaluation
## MYQUEUE=($(openQueue "myqueue"))
openQueue() {
  # Create named pipe
  local pipeName="/tmp/$1"
  mkfifo $pipeName

  # create file descriptors and redirect for read and write
  local queue=( $((QUEUE_MIN++)) $((QUEUE_MIN++)) )
#  exec ${queue[$QUEUE_WRITE_FD]}>${pipeName}
#  exec ${queue[$QUEUE_READ_FD]}<${pipeName}
  exec 101>|${pipeName}
  exec 100<${pipeName}

  echo "${queue[@]}"
}

## Closes a queue by closing its input and output file descriptors and deleting its file.
## Receives the queue to close
closeQueue() {
  local queue=$1

  exec ${queue[$QUEUE_READ_FD]} <&-
  exec ${queue[$QUEUE_WRITE_FD]} <&-

  rm -q ${queue[$QUEUE_PIPE_PATH]}

}

## Reads an item from a queue.
## Receives the queue to read from
## returns the item readed. It must be called using evaluation
## DATA=$(readQueue $MYQUEUE)
readQueue() {
  local data
  local queue=$1
  read -u ${queue[$QUEUE_READ_FD]} data

  echo "$data"
}


## Writess an item to a queue.
## Receives the queue to write to and the item to write.
## writeQueue $MYQUEUE "Peacho de dato"
writeQueue() {
  local fd=${1[$QUEUE_WRITE_FD]}
  echo "$2" >&${fd}
}
