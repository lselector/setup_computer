#! /bin/bash

echo "git repo size in MB"

cd $HOME/Documents/GitHub

for mydir in $(cat ~/Documents/GitHub/setup_computer/my_git_repositories.txt)
do
    du -sm $mydir | awk '{printf "%4d %s\n", $1, $2}'
done
echo "ALL DONE"
