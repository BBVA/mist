
printOut() {
  local queueIn=$1
  local data=$(readQueue $queueIn)
  while [[ $data != "END" ]]
  do
    echo $data
    data=$(readQueue $queueIn)
  done

}
