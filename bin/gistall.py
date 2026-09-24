#! /usr/bin/env python3

"""
# gistall.py
# checks status of all git repos found in
#   ~/Documents/GitHub/*  and  ~/Documents/GitHub/*/*
# It effectively runs "gist" command in all repos directories.
# To use it, create a shell wrapper "bin/gistall"
#    chmod +x ~/bin/gistall
#
# Usage:
#   gistall          # fetch, diff, status in every repo
#   gistall -v       # verbose output
#   gistall -u       # pull updates from remote
#   gistall -l       # list found git repos and exit
#
# Updated: 2026-09-24 (auto-discover repos, drop ~/.gistall)
"""

import os
import sys
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

import re
import argparse

import ipython_debug
from ipython_debug import *

import mybag
from mybag import *

import myutil
from myutil import *

ROOT_DIR = "Documents/GitHub"

# ---------------------------------------------------------------
def make_cmd_template(bag):
    """
    # returns template string with shell commands
    """
    ss = """cd "__REPO_DIR__"; echo "__SEP__" `pwd`;""" 
    if bag.update_from_remote:
        ss += """ git stash clear;
                  git stash -q;
                  git pull;
                  stashes=`git stash list | wc -l`;
                  if [ $stashes -ne 0 ]; then git stash apply; fi;"""
        ss = ss.replace("__SEP__", bag.sep)
        ss = re.sub(r'\s+', ' ', ss)
        return ss
    # ----------------------------------
    # if we are here - we will do gist
    if not bag.verbose:
        ss += """ git fetch -q; 
                  git diff --name-status ;
                  git status -s . ;"""
    else:
        ss += """
        echo "__SEP__ files which diff from remote repo";
        git fetch;
        git diff --name-status ;
        echo "__SEP__ files changed locally";
        git status . ;
        echo "__SEP__" ; """
    
    ss = ss.replace("__SEP__", bag.sep)
    ss = re.sub(r'\s+', ' ', ss)

    return ss


# ---------------------------------------------------------------
def process_cmd_args(bag):
    """
    # process cmd line arguments
    """
    descr_str = f"""Script to check status of all repos under {ROOT_DIR}
        by running git fetch, diff, and status in subdirectories"""
    parser = argparse.ArgumentParser(description=descr_str)
    parser.add_argument('--verbose', '-verbose', '-v', 
        action='store_true',  dest='arg_verbose', default=False,
        help="flag to get more verbose output")
    parser.add_argument('--update', '-update', '-u', 
        action='store_true',  dest='arg_update', default=False,
        help="update from remote server")
    parser.add_argument('--list', '-list', '-l',
        action='store_true',  dest='arg_list', default=False,
        help="list git repos found and exit")
    bag.arg_raw = parser.parse_args()
    bag.verbose = bag.arg_raw.arg_verbose
    bag.update_from_remote = bag.arg_raw.arg_update
    bag.list_repos = bag.arg_raw.arg_list

# ---------------------------------------------------------------
def subdirs(parent):
    """Return sorted names of non-hidden subdirectories."""
    return sorted(
        d for d in os.listdir(parent)
        if not d.startswith('.')
        and os.path.isdir(os.path.join(parent, d)))

# ---------------------------------------------------------------
def set_bag_repo_dirs(bag):
    """Set bag.repo_dirs to git repos at depth 1 and 2."""
    is_repo = lambda rel: os.path.exists(
        os.path.join(bag.root_dir, rel, ".git"))
    mylist = []
    for top in subdirs(bag.root_dir):
        if is_repo(top):
            mylist.append(top)
        for sub in subdirs(os.path.join(bag.root_dir, top)):
            rel = top + "/" + sub
            if is_repo(rel):
                mylist.append(rel)
    bag.repo_dirs = mylist

# ---------------------------------------------------------------
def myexit(bag):
    """
    # returns to initial directory 
    # and exists with proper return code
    """
    os.chdir(bag.init_dir)
    sys.exit(bag.error_flag)

# ---------------------------------------------------------------
def chdir_to_gh(bag):
    """
    # cd into ROOT_DIR directory
    """    
    if not os.path.isdir(bag.root_dir):
        print("ERROR, directory '%s' doesn't exist, Exiting ..." % bag.root_dir)
        bag.error_flag = 1
        myexit(bag)
    
    os.chdir(bag.root_dir)
    
    # check that we are in correct directory
    if os.getcwd() != bag.root_dir:
        print("ERROR, script only runs from '%s' directory. Exiting ..." % bag.root_dir)
        bag.error_flag = 1
        myexit(bag)

# --------------------------------------------------------------
def my_run_cmd(bag, mycmd, verbose=True, mask_error=False):
    """
    # runs command, prints status line
    # if error, sets bag.error_flag
    """
    if verbose:
        print('running ' + mycmd)
    try:
        bag.retcode = subprocess.call(mycmd, shell=True)
        if bag.retcode == 0:
            print("SUCCESS, process return code = " + str(bag.retcode))
        else:
            bag.error_flag = 1
            print("ERROR, process return code = " + str(bag.retcode))

    except Exception:
        bag.error_flag = 1
        print("ERROR, script failed with exception")

# ---------------------------------------------------------------
def main(bag):
    """
    # main execution
    """
    bag.error_flag = 0
    bag.sep = "-"*36
    process_cmd_args(bag)
    bag.init_dir = os.getcwd() # initial directory
    bag.home = os.path.expanduser("~")
    bag.root_dir = bag.home + "/" + ROOT_DIR
    chdir_to_gh(bag)
    set_bag_repo_dirs(bag)

    if bag.list_repos:
        print("\n".join(bag.repo_dirs))
        myexit(bag)

    bag.cmd_template = make_cmd_template(bag)
    for repo_dir in bag.repo_dirs:
        mycmd = bag.cmd_template.replace("__REPO_DIR__",repo_dir).strip()
        if bag.verbose:
            print(mycmd,"\n")
        my_run_cmd(bag, mycmd, verbose=False)

    myexit(bag)

# ---------------------------------------------------------------
# main execution
# ---------------------------------------------------------------
if __name__ == "__main__":
    bag = MyBunch()
    main(bag)
