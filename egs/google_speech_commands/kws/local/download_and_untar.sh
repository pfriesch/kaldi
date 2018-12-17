#!/bin/bash

#TODO

remove_archive=false

if [ "$1" == --remove-archive ]; then
  remove_archive=true
  shift
fi


data=$1
url=$2
dataset_name=$3

if [ ! -d "$data" ]; then
  echo "$0: no such directory $data"
  exit 1;
fi

data=$(readlink -f $data)

#TODO
if [ -z "$url" ]; then
  echo "$0: empty URL base."
  exit 1;
fi


#TODO

if [ ! -f $data/dataset_name.tar.gz ]; then
  if ! which wget >/dev/null; then
    echo "$0: wget is not installed."
    exit 1;
  fi
  full_url=$url/dataset_name.tar.gz
  echo "$0: downloading data from $full_url.  This may take some time, please be patient."

  cd $data
  if ! wget --no-check-certificate $full_url; then
    echo "$0: error executing wget $full_url"
    exit 1;
  fi
  cd -
fi

cd $data

if ! tar -xvzf $dataset_name.tar.gz; then
  echo "$0: error un-tarring archive $data/$dataset_name.tar.gz"
  exit 1;
fi

touch $data/LibriSpeech/$dataset_name/.complete

echo "$0: Successfully downloaded and un-tarred $data/$dataset_name.tar.gz"

if $remove_archive; then
  echo "$0: removing $data/$dataset_name.tar.gz file since --remove-archive option was supplied."
  rm $data/$dataset_name.tar.gz
fi
