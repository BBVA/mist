
callFestin() {

  local TOR=""
  local domain=$1
  local dnsSrv=$2

  if [ "$3" == "True" ]
  then
    TOR="--tor"
  fi

  if [[ $# -gt 3 ]]
  then
    local queueOut=$4
  fi
  festin $domain $TOR -ds $dnsSrv | grep "Adding" | awk '{ print $8 }' | sed "s/'//g" | \
  while read data
  do
    if [[ -n $queueOut ]]
    then
      writeQueue $queueOut "$data"
    else
      echo $data
    fi
  done
}
