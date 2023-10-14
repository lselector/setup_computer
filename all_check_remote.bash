#! /bin/bash

# set -x    # show commands 

for mydir in $(cat ~/Documents/GitHub/setup_computer/my_git_repositories.txt)
do
    cd $HOME/Documents/GitHub/$mydir
    git remote -v     # show remote
    git branch        # show branch(es)
done
