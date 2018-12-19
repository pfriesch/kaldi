#!/bin/bash


remove_archive=false

if [ "$1" == --remove-archive ]; then
  remove_archive=true
  shift
fi

data=$1
url=$2
dataset_name=$3


#TODO check for downloaded zip

if [ ! -f $data/$dataset_name.complete ]; then
    cd $data

    if [ ! -f $dataset_name.tar.gz ]; then
      if ! which wget >/dev/null; then
        echo "$0: wget is not installed."
        exit 1;
      fi
      full_url=$url/$dataset_name.tar.gz
      echo "$0: downloading data from $full_url.  This may take some time, please be patient."

      if ! wget --no-check-certificate $full_url; then
        echo "$0: error executing wget $full_url"
        exit 1;
      fi
    fi

    if [ ! -d $dataset_name ]; then
    mkdir $dataset_name
    fi

    if ! tar -xvzf $dataset_name.tar.gz -C $dataset_name; then
      echo "$0: error un-tarring archive $data/$dataset_name.tar.gz"
      exit 1;
    fi

    touch $dataset_name.complete

    echo "$0: Successfully downloaded and un-tarred $data/$dataset_name.tar.gz"

    if $remove_archive; then
      echo "$0: removing $data/$dataset_name.tar.gz file since --remove-archive option was supplied."
      rm $data/$dataset_name.tar.gz
    fi
else
echo "speech commands dataset already downloaded and extracted. Skipping..."
fi