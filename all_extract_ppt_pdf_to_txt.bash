#! /bin/bash

# list of repositories (code_samples, crypto, etc.)
# is in file

MYREPOS="$HOME/Documents/GitHub/setup_computer/my_git_repositories.txt"


for mydir in $(cat $MYREPOS)
do
    cd $HOME/Documents/GitHub/$mydir
    pwd
    python  ../setup_computer/ppt2txt.py ./
    python  ../setup_computer/pdf2txt.py ./
    cd ..
done
