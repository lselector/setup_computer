#! /bin/env python

"""
# myutil.py - misc. utility functions (not NZ related)
# Created in November 2014 by Lev Selector
"""

import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
# -------------------------------------
import sys
if sys.version_info < (3,3):
    sys.exit(1)
# -------------------------------------
import importlib
import argparse                   # parse cmd options
import re                         # regular expressions
# --------------------------------------
import time
import datetime as dt
# --------------------------------------
import subprocess
import socket
import inspect
# --------------------------------------
import uuid                       # for generating unique identifiers
import glob
# --------------------------------------
import zipfile                    # for creating zip files
import zlib                       # for compressing contents of zip files
import importlib
import pickle
# --------------------------------------
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
pd.options.display.width           =  1000
pd.options.mode.chained_assignment =  None
# --------------------------------------
import ipython_debug
importlib.reload(ipython_debug)
from ipython_debug import *
# --------------------------------------
import mybag
importlib.reload(mybag)
from mybag import *
# --------------------------------------
import mylog
importlib.reload(mylog)
from mylog import *
# ---------------------------------------------------------------
def set_user_and_home(bag):
    """
    # set bag.user and bag.home
    """
    output   = subprocess.check_output('whoami', shell=True)
    words    = output.split()
    bag.user = words[0]
    bag.home = os.path.expanduser("~")

# ---------------------------------------------------------------
def timing_start(label):
    """
    # simple shortcut procedure - prints label, 
    # returns two values: (start_time, label)
    # typically used with timing_add()
    """
    print("start: " + label)
    return time.time(), label 

# ---------------------------------------------------------------
def timing_add(bag, label, duration):
    """
    # procedure to add duration to bag.timing
    """
    duration = round(duration,3)
    print("     %.3f sec - %s" % (duration, label))
    if not test_avail(bag,'timing'):
        bag.timing = []
    bag.timing.append((label, duration))

# ---------------------------------------------------------------
def timing(myfunc):
    """
    # decorator wrapper to calculate runtime and save it
    # into bag.timing, which is a list of tuples (func_name, duration)
    # Note: myfunc should receive "bag" as a first argument.
    # Usage:
    #   @timing
    #   def do_work(bag,...):
    #       #code
    """
    # ----------------------------------
    def wrap(*args, **kwargs):
        bag = args[0]
        time1 = time.time()
        ret = myfunc(*args, **kwargs)
        time2 = time.time()
        func_name = myfunc.func_name
        timing_add(bag, func_name, time2-time1)
        return ret

    return wrap

# ---------------------------------------------------------------
def print_timing(bag, exclude=None):
    """
    # prints contents of bag.timing as two columns:
    #    (func_name, run_time), for example:
    #    Timing:
    #                func1 :      0.08 sec
    #                func2 :      0.18 sec
    #      some_other_func :      0.30 sec
    #    etc.
    # optional parameter "exclude" is a dictionary with 
    # keys as function names to exclude from printing 
    """
    if not test_avail(bag,'timing'):
        return
    if len(bag.timing) <= 0:
        return
    if not exclude:
        exclude = dict()
    mylog(bag, "Timing:")
    # ----------------------------------
    # We are about to print two columns: labels - and times
    # To achieve vertical alignment, let's find the max length of the labels
    max_len = 10
    for entry in bag.timing:
        if len(entry[0]) > max_len:
            max_len = len(entry[0]) + 1
    # Now we can use this max_length to format columns
    format_str = "%" + "%d" % max_len + "s : %10.3f sec"
    for entry in bag.timing:
        if entry[0] in exclude:
            continue
        mylog(bag, format_str % (entry[0], entry[1]))

# --------------------------------------------------------------
def print_func_name(bag):
    """
    # prints current function name
    # call this function as a first line in your function.
    """
    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    func_name = str(inspect.stack()[1][3])
    mylog(bag, "%s Doing %s" % (now_str, func_name))

# --------------------------------------------------------------
def get_func_name():
    """
    #
    """
    return inspect.stack()[1][3]

# ---------------------------------------------------------------
def myinit(bag):
    """
    # init operations
    # receives MyBunch object
    # adds some common fields, sets logging
    """
    bag.app = MyBunch()     # hide technical stuff here (not bus. data)
    bag.app.script_start_time = time.time()

    # ---- script name
    full_name  = sys.argv[0]
    short_name = full_name.split('/')[-1]
    bag.app.full_script_name  = full_name
    bag.app.short_script_name = short_name
    bag.app.script_cmd        = "python -uB %s" % (' '.join(sys.argv))

    # ---- init some common bag elements
    bag.app.files    = MyBunch()
    bag.app.db_conns = MyBunch()
    bag.app.cfg      = MyBunch()
    bag.errors = ""
    bag.exclude = dict()

# --------------------------------------------------------------
def slurp(fname):
    """
    # accepts file name
    # read text file - and return it as one string
    """
    fh = open(fname)
    txt = fh.read()
    fh.close()
    return txt

# --------------------------------------------------------------
def tofile(obj,fname):
    """
    # prints any object as string to a text file
    # Exampel: tofile(df, "junk.txt")
    # Example: /tofile  df  'junk.txt'
    # notice leading "/" to tell ipython that this is a function call
    """
    ss= str(type(obj))
    if re.search(r'Series|DataFrame',ss):
        mystr = obj.to_string()
    else:
        mystr = obj.__str__()
    f=open(fname,'w')
    f.write(mystr)
    f.close()

# --------------------------------------------------------------
def get_unique_id_str():
    """
    # creates a unique string - something like this '212d1f1c-fdbd-11e1-b7b6-00163e03ffbf'
    """
    return str(uuid.uuid1())

# --------------------------------------------------------------
def run_cmd(bag, mycmd, verbose=True, mask_error=False):
    """
    # runs command, prints status line
    # if error, sets bag.error_flag and includes
    # the word ERROR in printout without masking it
    """
    if verbose:
        mylog(bag, 'running ' + mycmd)
    try:
        bag.retcode = subprocess.call(mycmd, shell=True)
        if bag.retcode == 0:
            ss = "SUCCESS, process return code = " + str(bag.retcode)
            mylog(bag, ss)
        else:
            bag.error_flag = 1
            ss = "ERROR, process return code = " + str(bag.retcode)
            mylog(bag, ss, mask_log=mask_error)

    except Exception:
        bag.error_flag = 1
        ss = "ERROR, script failed with exception"
        mylog(bag, ss, mask_log=mask_error)


# --------------------------------------------------------------
def zip_a_file(filename, name_in_zip=None, dest_zip='/tmp/junk.zip'):
    """
    # compresses a filename into a new zip archive dest_zip
    # You can specify the name_in_zip,
    # for example name_in_zip = "somedir/"+basename(filename)
    """
    zf = zipfile.ZipFile(dest_zip, mode='w')
    zf.write(filename=filename, arcname=name_in_zip, compress_type=zipfile.ZIP_DEFLATED)
    zf.close()

# --------------------------------------------------------------
def zip_files(list_of_files, dest_zip='/tmp/junk.zip', list_in_zip=None):
    """
    # compresses a file into a new zip archive
    """
    if not list_in_zip:
        list_in_zip = []
    zf = zipfile.ZipFile(dest_zip, mode='w')
    for ii in range(len(list_of_files)):
        fname = list_of_files[ii]
        name_in_zip = None if len(list_in_zip) <=0 else list_in_zip[ii]
        zf.write(filename=fname, arcname=name_in_zip, compress_type=zipfile.ZIP_DEFLATED)
    zf.close()


# ---------------------------------------------------------------
def reset_8th_bit(ss):
    """
    # accepts a string ss
    # substitutes all chars with ord()>=128 by '*'
    # returns tuple (ss2, counter), where:
    #     ss2  - converted string
    #     counter - number of changed chars
    """
    return re.subn(r'[\x80-\xFF]', '*', ss)  # retunrs tuple

# ---------------------------------------------------------------
def calc_chk_digit(isbn13_str):
    """
    # accepts a string of digits representing ISBN-13
    # with or without the check digit
    # returns the correct check digit as a one character string.
    # returns None if provided string is not 12..13 chars long
    # Example of usage: calc_chk_digit('9780060099008')
    """
    if (len(isbn13_str) != 13) and (len(isbn13_str) != 12):
        return None
    sum1 = 0
    for ii in range(12):
        coef = 3 if (ii % 2) else 1
        sum1 += int(isbn13_str[ii]) * coef
    chk_digit = 10 - sum1 % 10
    chk_digit_str = '0' if chk_digit == 10 else str(chk_digit)

    return chk_digit_str

# ---------------------------------------------------------------
def is_valid_isbn13(isbn13_str):
    """
    # Returns true if the given string is a valid ISBN-13.
    """
    if len(isbn13_str) != 13:
        return False
    if not isbn13_str.isdigit():                # Check for all digits
        return False
    if not (isbn13_str[0:3] == '978' or isbn13_str[0:3] == '979'):
        return False                            # Must start with 978 or 979
    check_digit_str = calc_chk_digit(isbn13_str)
    if check_digit_str == None:                 # Check digit calc failed
        return False
    return check_digit_str == isbn13_str[-1]    # Compare correct check digit w/actual

# ---------------------------------------------------------------
def calc_prod_key(isbn13_str):
    """
    # acepts an ISBN-13 string that has been validated,
    # returns the prod_key, which is an integer.
    """
    if isbn13_str[0:3] == '978':
        return int(isbn13_str[3:12])   # 9-digit string
    elif isbn13_str[0:3] == '979':
        return int(isbn13_str[3:12]) + 1000000000
    else:
        raise Exception('Invalid ISBN prefix')

# ---------------------------------------------------------------
def rename_columns_to_lower_in_place(df):
    """
    # accepts DataFrame
    # renames its column names to lower case
    # does it "in place", returns nothing
    """
    mydict = dict([(ss,ss.lower()) for ss in df.columns])
    df.rename(columns=mydict, copy=False, inplace=True)

# --------------------------------------------------------------
def commify(n, show_cents=False):
    """
    # accepts money amount, adds commas
    # don't return cents by default
    """
    if n is None: return None
    if n < 0: return '-' + commify(-n,show_cents)
    n = round(n,2)               # only keep 2 digits for cents
    dollars = int(n)
    cents   = round((n - dollars)*100)
    dollars = '%d' % dollars
    cents   = '%02d' % cents
    groups = []
    while dollars and dollars[-1].isdigit():
        groups.append(dollars[-3:])
        dollars = dollars[:-3]
    ss = dollars + ','.join(reversed(groups))
    if show_cents :
        ss = ss + '.' + cents
    return ss

# --------------------------------------------------------------
def commify2(n):
    """
    # accepts money amount, adds commas, shows cents
    """
    return commify(n,True)

# --------------------------------------------------------------
def commify2_dollar(n):
    """
    # accepts money amount, adds commas, shows cents, prepends dollar sign
    """
    return "$" + commify2(n)

# --------------------------------------------------------------
def commify_test():
    """
    # tests/demonstrates how commify function is working
    """
    mylist = [ 0, 1, 123, 1234, 1234567890, 123.0, 1234.5, 1234.04,
                          1234.56789, 1234.99, 1234.999, -0, -1234.5678 ]
    for n in mylist:
        print('%012f => %s' % (n,commify(n)))

# --------------------------------------------------------------
def pickle_read(bag, fname):
    """
    # loads pickle file  - and returns the object
    # note - file was saved using pickle.dump() method
    """
    if(not os.path.isfile(fname)):
        print("pickle file  " + fname + "  doesn't exist, skipping ...")
        return None
    else:
        print("reading pickle file  " + fname)
        return pickle.load(open(fname, "rb"))

# --------------------------------------------------------------
def pickle_write(bag, obj, fname):
    """
    # writes object to pickle file using pickle.dump() method
    """
    print("saving object to pickle file:  " + fname)
    pickle.dump(obj, open(fname, "wb"), protocol=2)

# --------------------------------------------------------------
def memory_usage():
    """
    # Linux-specific function
    # returns memory usage of current process in KB
    # as a dict with 3 elements (vmpeak, vmrss, vmsize).
    # Function relies on file /proc/self/status
    # which contains lines like these:
    #    VmPeak:  5959660 kB
    #    VmSize:   492236 kB
    #    VmRSS:     49624 kB
    #    etc.
    """
    result = {'vmpeak': 0, 'vmrss': 0, 'vmsize': 0}
    fname = '/proc/self/status'
    try:
        for line in open(fname):
            parts = line.split()
            key = parts[0][:-1].lower() # 'VmPeak:' => 'vmpeak'
            if key in result:
                result[key] = int(parts[1])
    except:
        err_str = "Error getting memory usage from " + fname
        print(err_str)
        raise Exception(err_str)
    return result

# ---------------------------------------------------------------
def exit_with_error(bag, message):
    """
    # prints error message, prints error - and exits
    """
    print("\nError - ", message, "\nExiting...\nRun with --help to see help\n")
    sys.exit(1)

