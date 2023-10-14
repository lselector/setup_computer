"""
# -----------------------------------------------
# git_autosubmit.py
#
# called weekly to submit scripts to GitHub
#  .. generate list of files to submit
#  .. leave only sh, bash, py, txt
#  .. submit
#
# by Lev Selector, 2023
# -----------------------------------------------
"""

import os, sys, time, subprocess
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
from myutil import *
from myutil_dt import *

# ---------------------------------------------------------------
def myrun(cmd):
    """ simple function to run shell command and return a string """
    try:
        txt = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        txt = e.output
    txt = txt.decode().strip()
    return txt

# ---------------------------------------------------------------
def git_status(bag):
    """
    # runs  git add --dry-run .
    # it produces list of commands with "add" and "remove"
    # we change "remove" to "rm" - and store in bag.list_add_rm
    """
    cmd  = f"git add --dry-run . "
    mylist = myrun(cmd).split("\n")
    for ii in range(len(mylist)):
        elem = mylist[ii]
        if elem.startswith("remove "):
            mylist[ii] = "rm " + elem[7:]
    bag.list_add_rm = mylist

# ---------------------------------------------------------------
def select_ipynb(elem):
    """ select notebook files with size <=200K """
    # example:  "add 'dir1/note1.ipynb'"
    if elem.startswith("rm "):
        return True
    if not elem.endswith(".ipynb'"):
        return False
    parts = elem.split()
    if len(parts) !=2:
        return False
    fname = parts[1]
    fname = fname.replace("'","")
    file_size = os.path.getsize(fname) # in bytes
    if file_size < 215000:
        return True
    else:
        return False

# ---------------------------------------------------------------
def select_commands(bag):
    """
    # runs  git add --dry-run .
    """
    bag.cmd_selected = []
    bag.cmd_skipped = []
    for elem in bag.list_add_rm:
        # print("xxxx", elem)
        if ( elem.endswith(".py'") or elem.endswith("sh'")
             or elem.endswith(".txt'") or elem.endswith(".gitignore'")
             or elem.startswith("add 'bin/")
             or elem.startswith("rm ")
             or select_ipynb(elem)
             ):
            # print(f"adding{elem}")
            bag.cmd_selected += [elem]
        else:
            bag.cmd_skipped += [elem]

# ---------------------------------------------------------------
def submit_and_push(bag):
    """
    # runs git submit and git push
    """
    for ss in bag.cmd_selected:
        cmd = "git " + ss
        print(cmd)
        myrun("git " + ss)
    comment = 'submitted ' + now_str_for_log()
    cmd  = f"git commit -m'{comment}'"
    print(cmd)
    myrun(cmd)
    cmd = "git push"
    print(cmd)
    myrun(cmd)

# ---------------------------------------------------------------
def main(bag):
    """ main execution """

    # mylog(bag, "in main")
    os.chdir('/data/code')
    bag.cur_dir = os.getcwd()
    print(bag.cur_dir)
    git_status(bag)
    print(bag.list_add_rm)
    print("-"*50)
    select_commands(bag)
    print(f"SELECTED")
    for ee in bag.cmd_selected:
        print(ee)
    print("-"*50)
    print(f"SKIPPED")
    for ee in bag.cmd_skipped:
        print(ee)
    print("-"*50)
    submit_and_push(bag)
    print("-"*50)
    os.chdir('/data/code/misc')


# ---------------------------------------------------------------
# main execution
# ---------------------------------------------------------------
if __name__ == "__main__":
    bag  = MyBunch()
    bag.mask_log_str = ""
    myinit(bag)
    main(bag)

