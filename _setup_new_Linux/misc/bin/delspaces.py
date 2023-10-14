#---------------------------------------------------------------
#!/usr/bin/env python
"""
#---------------------------------------------------------------
# script delspaces.py
# designed to work on Unix systems (MacOS, Linux)
#
# put it into "bin" directory
# make it executable
# make a link  ln -s delspaces.py delspaces
# 
# Usage:
# open terminal in any working directory 
# and type command "delspaces"
# 
# The script will recursively remove spaces
# from file names under current directory
#---------------------------------------------------------------
# Why this script is useful?
# 
# When you use this common command:
# 
#   find ./ ...    | xargs grep  ... 
# 
# it will break on names with spaces in them
# because Unix treats each word as a separate file name
# 
# You can go around this problem using options 
# to use ASCII NUL character instead of space 
# to end (separate) the filenames
# 
#   -print0 option in find,
#   -0      option in xargs
# ```
# for example:
#   find ./ -type f -print0 | xargs -0 ls -1
# 
# but doing this every time is not convenient
# It is more convenient to use this script
# It can recursevely rename directories and files
# by substituting spaces, quotes, etc.
# by underscores
#---------------------------------------------------------------
"""
import sys, os, glob, subprocess, time, datetime
HOME  = os.environ['HOME']  # absolute path of home directory
MYDIR = os. getcwd()        # absolute path of current directory
#---------------------------------------------------------------
# directories on my Mac which I don't want to be touched
skip_list = [
    "Applications",
    "Applications (Parallels)",
    "Parallels",
    "Public",
    "VicsLogoMatcher",
    "brett_env",
    "gowork",
    "proj1_env",
    "test",
    "test2",
    "Google Drive",
    "Library",
    "Music/Music",
    "Pictures",
    "Movies",
    "Documents",
    "Calibre Library",
    "docs_big/SOFT_big",
    "docs/mySOFT_sn",
    "anaconda3"
]
skip_list = [HOME+"/"+x for x in skip_list] # absolute paths
#---------------------------------------------------------------
def print_date_time():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#---------------------------------------------------------------
def myrun(cmd):
    """
    # simple function to run shell command and return a string
    """
    try:
        txt = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        txt = e.output
    txt = txt.decode().strip()
    return txt
#---------------------------------------------------------------
def in_skip_list(myfile):
    """
    # checks if myfile (full path) is under a directory in skip_list
    """
    global MYDIR
    global skip_list
    skip_flag = False
    for elem in skip_list:
        if elem in MYDIR+"/"+myfile:
            skip_flag = True
    return skip_flag
#---------------------------------------------------------------
def rename_if_needed(myfile):
    """ 
    # renames file or directory (if needed)
    # returns 1 if rename was needed, or 0 if not needed 
    """
    myfile2 = myfile[:]
    myfile2 = (myfile2.replace(' ', '_')
                      .replace('"', '_')
                      .replace("'", '_')
                      .replace('&', '_'))
    if myfile2 == myfile:
        return 0
    print(f"renaming: {myfile} => {myfile2}")
    try:
        os.rename(myfile, myfile2) 
    except: 
        print("need to do more renaming")
    return 1
#---------------------------------------------------------------
def clean_names_directories():
    print(f"checking/cleaning directory names under {MYDIR=}")
    os.chdir(MYDIR)
    myflag = True
    mycount = 0
    while myflag == True and mycount < 10:
        mycount += 1
        print("getting list of all directories")
        out_str = myrun("/usr/local/bin/fd -t d")
        dirs1   = out_str.split("\n")
        print(f"N dirs1 = {len(dirs1):10,d}")
        #-------------------------------------------------------
        # remove directories which are in skip list"
        dirs = []
        for dd in dirs1:   # relative directories
            if in_skip_list(MYDIR+"/"+dd):
                continue
            dirs += [dd]
        print(f"N dirs  = {len(dirs1):10,d}")
        #-------------------------------------------------------
        # rename directories (spaces and quotes to underscores)
        N = len(dirs)
        counter = 0
        for mydir in dirs:
            counter += rename_if_needed(mydir)
        if counter >= 1:
            print(f"renamed {counter} directories, run again !")
            myflag = True
        else:
            print(f"no directories to rename, good")
            myflag = False
        print(f"finished loop # {mycount}")
#---------------------------------------------------------------
def clean_names_files():
    print(f"checking/cleaning file names under {MYDIR}")
    os.chdir(MYDIR)
    files1 = myrun("/usr/local/bin/fd -t f").split("\n")
    print(f"N files1 = {len(files1):10,d}")
    #----------------------------------------------------------
    # remove files which are in skip list"
    files = []
    for ff in files1:
        if in_skip_list(ff):
            continue
        files += [ff]
    print(f"N files  = {len(files):10,d}")
    N = len(files)
    counter = 0
    for ff in files:
        counter += rename_if_needed(ff)
    if counter >= 1:
        print(f"renamed {counter} files, run again !")
    else:
        print(f"no files to rename, good")
#---------------------------------------------------------------
# main execution
#---------------------------------------------------------------
if __name__ == "__main__":
    time1 = time.time()         # start time
    clean_names_directories()
    print("-"*40)
    clean_names_files()
    time2 = time.time()
    elapsed = time2-time1
    print(f"Elapsed seconds = {elapsed:.3f}")
#---------------------------------------------------------------
