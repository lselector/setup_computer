#! /bin/bash

# clean all git repositories by removing old commits

set -x    # show commands 

export MYDATE=`date +%Y%m%d`
export MYDT=`date +"%Y%m%d_%H%M%S"`

cd $HOME/Documents/GitHub

OLDDIR=OLD_$MYDT

# (re)create OLD directory
[ -d "$OLDDIR" ] && rm -rf $OLDDIR
mkdir $OLDDIR

for mydir in $(cat ~/Documents/GitHub/setup_computer/my_git_repositories.txt)
do
    echo "******************************************************"
    echo "starting working with $mydir"
    echo "******************************************************"
    cd $HOME/Documents/GitHub
    pwd
    rsync -a $mydir ./$OLDDIR/
    cd $mydir
    pwd
    git checkout --orphan latest_branch       # Switch to new branch 'latest_branch'
    git add -A                                # Add all files to this branch
    git commit -am "init"                     # Commit all files to this branch
    git branch -D master                      # Delete master branch
    git branch -m master                      # Rename branch as master
    git push -f --set-upstream origin master  # push to master branch
    git gc --aggressive --prune=all           # remove the old files
    cd ..
    pwd
done
echo " "
echo "ALL DONE"
echo " "
