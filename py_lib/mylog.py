#! /bin/env python

"""
# mylog.py 
#   mylog(bag,...) 
#   mylog_err(bag, ....)
"""

import os, sys
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
# --------------------------------------
import ipython_debug
from ipython_debug import *

import mybag
from mybag import *

# --------------------------------------------------------------
def mylog(bag, message="", log_flag=True, log_prefix=""):
    """
    # prepends prefix to (all) lines of the message 
    # and prints it out
    # options:
    #   log_flag (True of False) - to disable logging (if set to False)
    #   log_prefix (string) - string to prepend to all lines
    """
    if not log_flag:
        return
    if len(log_prefix):
        log_prefix = log_prefix + "  "
    mystr = str(message)
    mylist = mystr.split("\n")
    output = ""
    for ss in mylist:
        output += log_prefix + ss + "\n"
    print(output)

# ---------------------------------------------------------------
def mylog_err(bag, message=""):
    """
    # prints error message without masking it
    """
    mylog(bag, message=message, log_flag=True, log_prefix="ERROR")

