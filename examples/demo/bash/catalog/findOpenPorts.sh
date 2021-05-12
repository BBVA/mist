
## Guess if the given ports are open in the hosts received (from stdin or the
## input queue) and outputs the found ports through stdout or the output queue
findOpenPorts() {

  local ip
  local ports=$1

  if [ $# -gt 1 ]
  then
    local queueIn=$2

    if [ $# -gt 2 ]
    then
      local queueOut=$3
    fi
  fi

  if [[ -n $queueIn ]]
  then
    ip=$(readQueue $queueIn)
  else
    read ip
  fi
  while [[ $ip != "END" ]]
  do
    nmap -p "${ports}" --open ${ip} | awk '{print $1, $2, $3}' | grep open | \
    while read port status schema
    do
      local msg="{\"port\": ${port}, \"protocol\": \"$schema\"}"
      if [[ -n $queueOut ]]
      then
        writeQueue $queueOut "$msg"
      else
        echo $msg
      fi
    done

    if [[ -n $queueIn ]]
    then
      ip=$(readQueue $queueIn)
    else
      read ip
    fi
  done

  if [[ -n $queueOut ]]
  then
    writeQueue $queueOut "END"
  else
    echo "END"
  fi
}
