#!/usr/bin/env python
# coding: utf-8

# --------------------------------------------------------------
# Usage (unix only):
#     python remove_spaces.py dirname(s)
# If dirname is not provided - starts at current directory

# Recursively remove spaces from file names so that we 
# can use find ... | grep in terminal
#
# You can go around this problem using options 
# to use ASCII NUL character instead of space 
# to end (separate) the filenames
#   -print0 option in find,
#   -0      option in xargs
# for example:
#   find ./ -type f -print0 | xargs -0 ls -1
# --------------------------------------------------------------

import sys, os, glob, subprocess, time, datetime, re
# from ipython_debug import *     # debug_here()

time1 = time.time()

cwd = os.getcwd() # current working directory

if len(sys.argv) <= 1:
    mypath = os.getcwd()
    mypath = os.path.realpath(mypath)
    mydirs = [mypath]
else:
    mydirs = []
    for argpath in sys.argv[1:]:
        if not os.path.isdir(argpath):
            print(f"{argpath} is not a directory, exiting ...")
            sys.exit()
        mypath = os.path.realpath(argpath)
        print(argpath, "   =>  ", mypath)
        mydirs += [mypath]

# --------------------------------------------------------------
# we will process recursively only one directory
MYDIR = mydirs[0]
print(f"recursively processing directory {MYDIR}")
# --------------------------------------------------------------
# some system directories need to be skipped
HOMEDIR = os.environ['HOME'] + "/"
skip_list = [
    HOMEDIR+"Applications",
    HOMEDIR+"Applications (Parallels)",
    HOMEDIR+"anaconda3",
    HOMEDIR+"Calibre Library",
    HOMEDIR+"docs_big/SOFT_big",
    HOMEDIR+"docs/mySOFT_sn",
    HOMEDIR+"Documents",
    HOMEDIR+"Library",
    HOMEDIR+"Movies",
    HOMEDIR+"Music/Music",
    HOMEDIR+"Pictures"
]

# --------------------------------------------------------------
def print_date_time():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# --------------------------------------------------------------
# First clean directories' names layer by layer.
# May need to repeat it several times until there is no output.

print_date_time()
print(f"Getting list of directories under {MYDIR} - takes some time")
dirs = glob.glob(MYDIR+"/**/", recursive=True)

print_date_time()
N = len(dirs)
print(f"found {N:,d} dirs")
counter = 0
for mydir in dirs:
    # ------------------------------
    skip_flag = False
    for elem in skip_list:
        if elem in mydir:
            skip_flag = True
    if skip_flag:
        continue
    # ------------------------------
    if not os.path.isdir(mydir):
        continue
    if " " not in mydir:
        continue
    mydir2 = mydir.replace(" ","_")
    print(f"renaming: {mydir} => {mydir2}")
    os.rename(mydir, mydir2)
    counter += 1

if counter >= 1:
    print(f"renamed {counter} directories, run again !")
else:
    print(f"no directories to rename, good")
        
print("DONE cleaning directories")

# Next we can rename files to remove spaces, quotes, double quotes, "&".

# --------------------------------------------------------------
def rename_if_needed(myfile):
    mydir = os.path.dirname(myfile)
    basef = os.path.basename(myfile)
    myfile2 = basef[:]
    if " " in myfile2:
        myfile2 = myfile2.replace(" ","_")
    if "'" in myfile2:
        myfile2 = myfile2.replace("'","_")
    if '"' in myfile:
        myfile2 = myfile2.replace('"',"_")
    if '&' in myfile:
        myfile2 = myfile2.replace('&',"_")
    if re.search(r"\w__+", myfile2):
        myfile2 = re.sub(r"(\w)__+", r"\1_", myfile2)
    if re.search(r"_+\.", myfile2):
        myfile2 = re.sub(r"_+\.",r".",myfile2)
    myfile2 = mydir + "/" + myfile2
    if myfile2 != myfile:
        print(f"renaming: {myfile} => {myfile2}")
        os.rename(myfile, myfile2) 

# --------------------------------------------------------------
def in_skip_list(myfile):
    skip_flag = False
    for elem in skip_list:
        if elem in myfile:
            skip_flag = True
    return skip_flag

# --------------------------------------------------------------
# Run the code below repeatedly until there is no output

print_date_time()
print(f"Getting list of files under {MYDIR} - takes some time")
files = glob.glob(MYDIR+"/**", recursive=True)
print_date_time()
N = len(files)
N_step = N//10
print(f"found {N:,d} files")
print(f"printing after every {N_step:,d} files")
for ii in range(N):
    # print(f"processing file {files[ii]}")
    if N_step > 0 and (ii % N_step) == 0 and (ii > 0) :
        print(f"processing file # {ii:,d} of {N:,d}")
    myfile = files[ii]
    if in_skip_list(myfile):
        continue
    if not os.path.isfile(myfile):
        continue
    rename_if_needed(myfile)

print_date_time()
print("DONE")

time2 = time.time()
elapsed = time2-time1
print(f"Elapsed seconds = {elapsed:.3f}")

