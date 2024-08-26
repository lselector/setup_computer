#! /bin/bash

cd /data/code
mylist=$(ls -1d proj*/)

for dd in $mylist; do
  echo "$dd"
  cd "/data/code/$dd"
  gist
  cd ..
done



