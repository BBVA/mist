
kafkaProducer() {

  local msg
  local SERVERS=$1
  local TOPIC=$2

  if [[ $# -gt 2 ]]
  then
    local queueIn=$3
  fi

  if [[ -n $queueIn ]]
  then
    msg=$(readQueue $queueIn)
  else
    read msg
  fi
  while  [[ $msg != "END" ]]
  do
    kafka-console-producer --broker-list $SERVERS --topic $TOPIC <<< $msg

    if [[ -n $queueIn ]]
    then
      msg=$(readQueue $queueIn)
    else
      read msg
    fi
  done
}
