
## Searches for the associated domains to the given one by using the crt.io database
## Receives an initial domain to search for and an optional queue to write found
## domains to. If the queue parameter is missing it writes to standard output
searchDomains() {

  local domain=$1

  if [ $# -eq 2 ]
  then
    local queue=$2
  fi

  dnsrecon -d ${domain} -t crt | awk '{ print $2, $3, $4 }' | grep -e '^A ' | \
  while read type name ip
  do
    if [[ $type == "A" ]]
    then
      if [[ -n $queue ]]
      then
        writeQueue $queue $name
      else
        echo "$name"
      fi
    fi
  done

  if [[ -n $queue ]]
  then
    writeQueue $queue "END"
  else
    echo "END"
  fi

}
