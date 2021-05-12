
s3Store() {

  local bucketUri=$1
  local queueIn=$2
  local data

  data=$(readQueue $queueIn)
  while [[ $data != "END" ]]
  do
    echo $data
    data=$(readQueue $queueIn)
  done | aws s3 cp - $bucketUri
}
