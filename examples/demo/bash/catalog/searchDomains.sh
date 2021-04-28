

searchDomains() {
  local domain=$1
  local queue=$2
  local mode=$3

  dnsrecon -d ${domain} | awk '{ print $2, $3, $4 }' | grep -e '^A ' | \
  while read type name ip
  do
    if [ "$type" == "A" ]
    then
      if [ "$mode" == "queue" ]
      then
        writeQueue $queue $name
      else
        echo "$name"
      fi
    fi
  done
}
