

findOpenPorts() {
  local ip=$1
  local ports=$2
  local queue=$3
  local queue2=$4
  local mode=$5
  local data

  data=$(readQueue $queue)
  while true
  do
    nmap -p ${ports} --open ${ip} | awk '{print $1, $2, $3}' | grep open | \
    while read port status schema
    do
      if [ "$mode" == "queue" ]
      then
        writeQueue $queue2 "{\"port\": ${port%/tcp}, \"protocol\": \"$schema\"}"
      else
        echo "{\"port\": ${port%/tcp}, \"protocol\": \"$schema\"}"
      fi
    done

    data=$(readQueue $queue)
    [[ -n $data ]] && break
}
