#! /bin/env python

"""
# myutil_dt.py - utility functions for date/time
# Created in Dec 2014 by Lev Selector
# Last modified in Aug 2020
# works for python version 3,3 or later
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
import time, re, socket
import datetime as dt
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

# --------------------------------------
import ipython_debug
importlib.reload(ipython_debug)
from ipython_debug import *
# --------------------------------------
import mylog
importlib.reload(mylog)
from mylog import *
# --------------------------------------

# --------------------------------------------------------------
def sec_to_hms(secs):
    """
    # converts seconds into string in format "HH:MM:SS"
    """
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    h_str = "%d"   % int(h)
    m_str = "%02d" % int(m)
    s_str = "%02.2f" % round(s,2)
    s_str = re.sub(r'\.00$','',s_str)
    return ':'.join([h_str,m_str,s_str])

# --------------------------------------------------------------
def days_in_month(mydate):
    """
    # accepts date as string 'YYYY-MM-DD'
    # returns number of days in this month
    # note - I could've used
    #   from calendar import monthrange
    #   monthrange(2012, 2)
    # but I didn't want to import yet another module
    """
    (y1, m1, d1) = mydate.split('-')
    mstart1  = "%4d-%02d" % (int(y1),int(m1))   # month as 'YYYY-MM'
    mstart2  = get_next_month(mstart1)          # next month as 'YYYY-MM'
    (y2, m2) = mstart2.split('-')

    dt1 = dt.date(int(y1), int(m1), 1)   # year, month, first day
    dt2 = dt.date(int(y2), int(m2), 1)   # year, month, first day
    
    return (dt2-dt1).days

# --------------------------------------------------------------
def utc_date_to_epoch_secs(date_str='1970-01-01'):
    """
    # accepts date as UTC date
    # returns UTC epoch_seconds 
    # (from the beginning of 1970 UTC epoch
    # to the beginning of this date at UTC)
    """
    # create a time structure without time zone information
    time_struct = time.strptime(date_str, '%Y-%m-%d')
    epoch_secs  = calendar.timegm(time_struct)
    return int(epoch_secs)

# --------------------------------------------------------------
def utc_datetime_to_epoch_secs(date_str='1970-01-01 00:00:00'):
    """
    # accepts date as UTC date
    # returns UTC epoch_seconds 
    # (from the beginning of 1970 UTC epoch
    # to the beginning of this date at UTC)
    """
    # create a time structure without time zone information
    time_struct = time.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    epoch_secs  = calendar.timegm(time_struct)
    return int(epoch_secs)

# --------------------------------------------------------------
def date_to_epoch_secs(date_str='1970-01-01'):
    """
    # converts LOCAL date string YYYY-MM-DD
    # to UTC epoch seconds (integer)
    """
    # create a time structure without time zone information
    time_obj = time.strptime(date_str, '%Y-%m-%d')
    # use time.mktime() which treats date as a local date 
    # (if no time zone information is provided) 
    epoch_secs = time.mktime(time_obj)

    return int(epoch_secs)

# --------------------------------------------------------------
def datetime_to_epoch_secs(date_str='1970-01-01 00:00:00'):
    """
    # converts LOCAL datetime string 'YYYY-MM-DD HH:MM:SS' 
    # to UTC epoch seconds (integer)
    """
    # create a time structure without time zone information
    time_obj = time.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    # use time.mktime() which treats date as a local date 
    # (if no time zone information is provided) 
    epoch_secs = time.mktime(time_obj)

    return int(epoch_secs)

# --------------------------------------------------------------
def epoch_secs_to_local_datetime_str(epoch_secs = 0):
    """
    # accepts UTC epoch seconds (as integer or float)
    # returns local datetime string as YYYY-MM-DD HH:MM:SS
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_secs))

# --------------------------------------------------------------
def epoch_secs_to_local_date_str(epoch_secs = 0):
    """
    # accepts UTC epoch seconds (as integer or float)
    # returns local date string as YYYY-MM-DD
    """
    return time.strftime('%Y-%m-%d', time.localtime(epoch_secs))

# --------------------------------------------------------------
def epoch_secs_to_utc_datetime_str(epoch_secs = 0):
    """
    # accepts UTC epoch seconds (as integer or float)
    # returns UTC datetime string as YYYY-MM-DD HH:MM:SS
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch_secs))

# --------------------------------------------------------------
def epoch_secs_to_utc_date_str(epoch_secs = 0):
    """
    # accepts UTC epoch seconds (as integer or float)
    # returns UTC date string as YYYY-MM-DD
    """
    return time.strftime('%Y-%m-%d', time.gmtime(epoch_secs))

# --------------------------------------------------------------
def epoch_secs_now_float():
    """
    # gives current UTC epoch_secs as float
    """
    return time.time()

# --------------------------------------------------------------
def epoch_secs_now_int():
    """
    # gives current UTC epoch_secs as integer
    """
    return int(round(time.time()))

# --------------------------------------------------------------
def elapsed_time(bag, t1=None):
    """
    # returns time elapsed from beginning of the script in seconds
    # optionally accepts another starting point (in epoch seconds)
    # usage:
    #   tdiff = elapsed_time(bag)
    #   tdiff = elapsed_time(bag, t1=start_in_epoch_secs)
    """
    if t1 == None:
        t1 = bag.app.script_start_time
    t2 = time.time()
    mydiff = round(t2-t1,2)
    return mydiff

# --------------------------------------------------------------
def elapsed_time_hms(bag, t1=None):
    """
    # returns time elapsed from beginning of the script as string:
    #   HH:MM:SS , or HH:MM:SS.DD
    # optionally accepts another starting point (in epoch seconds)
    # usage:
    #   hms_str = elapsed_time(bag)
    #   hms_str = elapsed_time(bag, t1=start_in_epoch_secs)
    """
    return sec_to_hms(elapsed_time(bag, t1))

# --------------------------------------------------------------
def now_str():
    """
    # returns current date-time as a string like this: 2013-09-06 18:11:43
    """
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------------------------------------------------------------
def now_str_for_log():
    """
    # returns current date-time as a string like this: YYYYMMDD_HHMMSS,
    # for example: 20130906_181143
    """
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")

# --------------------------------------------------------------
def print_start_time(bag):
    """
    # prints current date/time
    # usage:
    #   print_start_time(bag)
    """
    time_now   = now_str()
    script_cmd = bag.app.script_cmd
    mylog(bag,"%s STARTED  ( %s )" % (time_now, script_cmd))

# --------------------------------------------------------------
def print_elapsed_time(bag, t1=None):
    """
    # prints current date/time, and time elapsed from beginning of the script
    # optionally accepts another starting point (in epoch seconds)
    # depends on bag.app.script_start_time and bag.app.script_cmd
    # which are created by calling myinit(bag)
    # usage:
    #   print_elapsed_time(bag)
    #   print_elapsed_time(bag, t1=start_in_epoch_secs)
    """
    time_now   = now_str()
    if not t1:
        t1 = bag.app.script_start_time
    elapsed    = elapsed_time_hms(bag, t1)
    script_cmd = bag.app.script_cmd
    mylog(bag,"%s FINISHED ( %s ), elapsed time was %s" % (time_now, script_cmd, elapsed))

# --------------------------------------------------------------
def print_current_date_time(bag):
    """
    # prints current date/time using mylog() function
    """
    time_now   = now_str()
    mylog(bag, time_now)

# --------------------------------------------------------------
def days_start_to_end(bag):
    """
    # returns number of days for which we run report.
    # if it is daily report - returns 1
    # for monthly - returns number of days in this month
    """
    start_date = dt.datetime.strptime(bag.start_date,'%Y-%m-%d')
    end_date   = dt.datetime.strptime(bag.end_date,  '%Y-%m-%d')
    return (end_date - start_date).days

# --------------------------------------------------------------
def get_date_shifted_by_days(start_date, num_days):
    """
    # accepts and returns date as string YYYY-MM-DD 
    # also accepts shift (in days, int)
    """
    return (dt.datetime.strptime(start_date,'%Y-%m-%d') + dt.timedelta(num_days)).strftime('%Y-%m-%d')

# --------------------------------------------------------------
def get_prev_date(ss):
    """
    # accepts and returns date as string YYYY-MM-DD
    """
    return (dt.datetime.strptime(ss,'%Y-%m-%d') - dt.timedelta(1)).strftime('%Y-%m-%d')

# --------------------------------------------------------------
def get_next_date(ss):
    """
    # accepts and returns date as string YYYY-MM-DD
    """
    return (dt.datetime.strptime(ss,'%Y-%m-%d') + dt.timedelta(1)).strftime('%Y-%m-%d')

# --------------------------------------------------------------
def get_day_only(ss):
    """
    # accepts YYYY-MM-DD, returns DD
    """
    (y, m, d) = ss.split('-')
    return "%02d" % (int(d))

# --------------------------------------------------------------
def get_month_only(ss):
    """
    # accepts YYYY-MM-DD, returns MM
    """
    (y, m, d) = ss.split('-')
    return "%02d" % (int(m))

# --------------------------------------------------------------
def get_year_month(ss):
    """
    # accepts YYYY-MM-DD, returns YYYY-MM
    """
    (y, m, d) = ss.split('-')
    return "%4d-%02d" % (int(y),int(m))

# --------------------------------------------------------------
def month_name(mm):
    """
    # accepts month number as int or string ('01, 02, etc)
    # returns motnh name
    """
    m = int(mm)
    mnames = ['January','February','March','April','May','June','July','August',
                        'September','October','November','December']
    return mnames[m-1]

# --------------------------------------------------------------
def get_year_only(ss):
    """
    # accepts YYYY-MM-DD, returns YYYY
    """
    (y, m, d) = ss.split('-')
    return "%4d" % (int(y))

# --------------------------------------------------------------
def get_next_month(ss):
    """
    # accepts and returns month as string YYYY-MM
    """
    (y, m) = ss.split('-')
    y = int(y)
    m = int(m)
    m = m + 1
    if m>12:
        m=1
        y=y+1
    return "%4d-%02d" % (y,m)

# --------------------------------------------------------------
def get_prev_month(ss):
    """
    # accepts and returns month as string YYYY-MM
    """
    (y, m) = ss.split('-')
    y = int(y)
    m = int(m)
    m = m - 1
    if m < 1:
        m = 12
        y=y-1
    return "%4d-%02d" % (y,m)

# --------------------------------------------------------------
def get_current_date():
    """
    # returns current date as string YYYY-MM-DD
    """
    yyyy,mm,dd = str(date.today()).split('-')
    return "%s-%s-%s" % (yyyy,mm,dd)

# --------------------------------------------------------------
def get_current_month():
    """
    # returns current month as string YYYY-MM
    """
    yyyy,mm,dd = str(date.today()).split('-')
    return "%s-%s" % (yyyy,mm)

# --------------------------------------------------------------
def current_year():
    """
    # returns year as a 4-digit string
    """
    return str(date.today()).split('-')[0]

# --------------------------------------------------------------
def current_month():
    """
    # returns month as a 2-digit string
    """
    return str(date.today()).split('-')[1]

# --------------------------------------------------------------
def current_day():
    """
    # returns day of the month as a 2-digit string
    """
    return str(dt.date.today()).split('-')[2]

# --------------------------------------------------------------
def date_month_start_current():
    """
    # returns date as YYYY-MM-01
    """
    return '-'.join([current_year(),current_month(),'01'])

# --------------------------------------------------------------
def date_month_start_next(mydt=''):
    """
    # accepts optional date
    # returns date as YYYY-MM-01
    """
    if mydt=='':
        yy = current_year()
        mm = current_month()
    else:
        ar = mydt.split('-')
        yy,mm = ar[:2]
    return get_next_month(yy + '-' + mm) + '-01'

# --------------------------------------------------------------
def date_month_start_prev():
    """
    # returns date as YYYY-MM-01
    """
    return get_prev_month(current_year() + '-' + current_month()) + '-01'

# --------------------------------------------------------------
def yyyymm(ss):
    """
    # accepts YYYY-MM-DD, returns YYYY-MM
    """
    (y, m, d) = ss.split('-')
    return "%4d-%02d" % (int(y),int(m))

# --------------------------------------------------------------
def month2short(month):
    """
    # accepts string in format 'YYYY-MM'
    # returns string in format 'yYYmMM'
    """
    ss = month
    ss = re.sub(r'^20','y',ss)
    ss = re.sub(r'\-' ,'m',ss)
    return ss

# --------------------------------------------------------------
def month2long(month):
    """
    # accepts string in format 'yYYmMM'
    # returns string in format 'YYYY-MM'
    """
    ss = month
    y,m=ss.replace('y','').split('m')
    ss = "20%s-%s" % (y,m)
    return ss

# --------------------------------------------------------------
def get_next_month_short(short_month, n=1):
    """
    # accepts month in short notation yYYmMM
    # optionally accepts number of months to shift by
    # returns month in short notation which is n-months after
    """
    long_month = month2long(short_month)
    for ii in range(n):
        long_month = get_next_month(long_month)
    return month2short(long_month)

# --------------------------------------------------------------
def get_prev_month_short(short_month, n=1):
    """
    # accepts month in short notation yYYmMM
    # optionally accepts number of months to shift by
    # returns month in short notation which is n-months earlier
    """
    long_month = month2long(short_month)
    for ii in range(n):
        long_month = get_prev_month(long_month)
    return month2short(long_month)

# --------------------------------------------------------------
def get_prev_quarter_dates(date_str):
    """
    # accepts date string YYYY-MM-DD
    # returns 2 dates in same format defining the previous quarter.
    # for example for '2013-01-05' it returns ('2012-10-01', '2013-01-01')
    """
    yyyy,mm,dd = date_str.split('-')
    yyyy = int(yyyy)
    mm = int(mm)
    qt = int((mm-1)/3.)
    if qt <=0:
        qt = 4
        yyyy -= 1
    if qt in [1,2,3]:
        m1 = (qt-1)*3 + 1
        y1 = yyyy
        m2 = m1 + 3
        y2 = yyyy
    else:
        m1 = 10
        y1 = yyyy
        m2 = 1
        y2 = yyyy + 1

    d1 = "%d-%02d-01" % (y1,m1)
    d2 = "%d-%02d-01" % (y2,m2)

    return d1,d2

# --------------------------------------------------------------
def fix_date(yyyy,mm,dd):
    """
    # receives year, month, day as integers or strings
    # (if strings - convert to int)
    # checks that the date is "sane" (doesn't check correct,
    # returns integers
    """
    yyyy = int(yyyy)
    mm   = int(mm)
    dd   = int(dd)
    try:
        dt.datetime(year=yyyy,month=mm,day=dd,hour=1)
    except:
        print("wrong date: (%4d-%2d-%2d)" % (yyyy,mm,dd))
        raise
    return (yyyy,mm,dd)

# --------------------------------------------------------------
def fix_date_str(date_str):
    """
    # check that the date is correct - and formats it properly
    """
    res = re.search("^(20\d\d)-?(\d{1,2})-?(\d{1,2})$", date_str)
    if not res:
        print("ERROR - date (%s) has to be as YYYY-MM-DD or YYYYMMDD, exiting" % date_str)
        raise
    yyyy = res.group(1)
    mm = res.group(2)
    dd = res.group(3)
    (yyyy,mm,dd) = fix_date(yyyy,mm,dd)
    return "%4d-%02d-%02d" % (yyyy, mm, dd)

# --------------------------------------------------------------
def date_from_date_key(date_key=None):
    """
    # accepts date_key as a integer nubmer of days since 1910-12-31
    # returns date in format 'YYYY-MM-DD'
    # note: for date_key=1 returns '1911-01-01'
    # note: 1911-01-01 was Sunday
    """
    dk = int(date_key)
    return get_date_shifted_by_days('1910-12-31', dk)

# --------------------------------------------------------------
def calc_date_key(date_str=None):
    """
    # accepts date_str in YYYY-MM-DD format
    # returns integer date_key as nubmer of days since 1910-12-31
    # example:
    #    calc_date_key('1911-01-01') # returns 1
    #    calc_date_key('2015-03-24') # returns 38069
    # note: 1911-01-01 was Sunday
    """
    dt_orig = dt.datetime.strptime(date_str    ,'%Y-%m-%d')
    dt_base = dt.datetime.strptime('1910-12-31','%Y-%m-%d')
    return (dt_orig - dt_base).days

# --------------------------------------------------------------
def date_valid(date_str=None, fmt='%Y-%m-%d'):
    """ 
    # checks if date_str is a valid date
    # by default expects date as YYYY-MM-DD
    # Examples of usage:
    #   date_valid('2015-03-24')
    #   date_valid('03/24/2015','%m/%d/%Y')
    """
    try:
        dt.datetime.strptime(date_str, fmt)
        return True
    except:
        return False
 
# --------------------------------------------------------------
def get_last_sunday(date_str=None):
    """ 
    # accepts a date.
    # by default (with no parameters), assumes current date.
    # returns the date string of the last Sunday <= input date
    # format: YYYY-MM-DD
    # Examples of usage:
    #   get_last_sunday()
    #   get_last_sunday('2015-04-19') # '2015-04-19'
    #   get_last_sunday('2015-04-18') # '2015-04-12'
    """
    mystr = get_current_date() if not date_str else date_str
    (y1, m1, d1) = mystr.split('-')
    mydate = date(int(y1), int(m1), int(d1))
    wday_idx = mydate.weekday()  # returns 6 for Sunday, 0 for Monday
    if wday_idx >= 6:
        return mystr
    else:
        myshift = wday_idx + 1
        return get_date_shifted_by_days(mystr, -myshift)

# --------------------------------------------------------------
def ascii_datetime(epoch_seconds):
    """
    # accepts epoch_seconds (integer like this: 1439338816)
    # returns date-time string '%Y-%m-%d %H:%M:%S'
    """
    return dt.datetime.fromtimestamp(epoch_seconds).strftime('%Y-%m-%d %H:%M:%S')

# --------------------------------------------------------------
def ascii_date(epoch_seconds):
    """
    # accepts epoch_seconds (integer like this: 1439338816)
    # returns date string '%Y-%m-%d'
    """
    return dt.datetime.fromtimestamp(epoch_seconds).strftime('%Y-%m-%d')

# --------------------------------------------
def my_days_offset(dt0, days_offset, bus_day_flag=False):
    """
    # accepts dt0 as type pandas._libs.tslibs.timestamps.Timestamp
    # takes date portion of it
    # applies days_offset - integer number
    # returns date as type pandas._libs.tslibs.timestamps.Timestamp
    # if bus_day_flag=True, it shifts by business days only
    """
    dt1 = dt.datetime.date(dt0)                                  # type datetime.date
    if bus_day_flag:
        dt2 = np.busday_offset(dt1,days_offset,roll='forward')   # type numpy.datetime64
    else:
        dt2 = dt1 + dt.timedelta(days=days_offset)                  # type datetime.date

    return pd.to_datetime(dt2)                                   # type pandas._libs.tslibs.timestamps.Timestamp

np.datetime64('2009') + np.timedelta64(20, 'D')

