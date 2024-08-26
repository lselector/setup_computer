#! /bin/env python

"""
# iolog.py
# Usage from crontab:
# * * * * * /usr/local/bin/python iolog.py  /mydir/iotop_logs
# 
# uses iotop utility to write disk usage into daily log files
# requires one parameter - directory where to put the log files.
# runs for ~1hour, then exists
# switches rotating daily log files with ~1min precision
# restarted from cron
"""

import os, sys, datetime, time, subprocess, re
os.environ["PYTHONDONTWRITEBYTECODE"] = "1" 
os.environ["PYTHONUNBUFFERED"] = "1" 

# --------------------------------------------------------------
def my_real_user():
    """
    # shows your real personal user (even if you became other user)
    # uses the fact that command 'who am i' shows your real user name
    # (commands id, echo $USER, whoami will show sudo name)
    # Note - when running from crontab, command 'who am i'
    # returns empty string. So we use 'whoami' instead.
    """
    output = subprocess.check_output('who am i', shell=True)
    if len(output) <= 0:
        output = subprocess.check_output('whoami', shell=True)
    words = output.split()
    return words[0]

# ---------------------------------------------------------------
# check that the output directory is provided on cmd line
# ---------------------------------------------------------------
if len(sys.argv) < 2:
    print "ERROR - please provide iotop_log directory"
    print "Usage:  python iolog.py /mydir/iotop_logs"
    print "Exiting ..."
    sys.exit(1)

# ---------------------------------------------------------------
# check if the output directory exists
# ---------------------------------------------------------------
logdir = os.path.realpath(sys.argv[1])
if not os.path.isdir(logdir):
    print "ERROR - directory %s doesn't exist, Exiting ..." % logdir
    sys.exit(1)

# ---------------------------------------------------------------
# check that the process is not already running
# ---------------------------------------------------------------
myuser = my_real_user()
mycmd = "ps auxww"
mytxt = subprocess.check_output("ps auxww", shell=True)
mylines = mytxt.split("\n")
myruns = []
for line in mylines:
    if re.search('^' + myuser + r'.*iolog\.py.*' + logdir, line):
        myruns += [line]
# print myruns
N_run = len(myruns)
# print N_run
if N_run > 1:
    # print "the service is already running, exiting"
    sys.exit(0)

# ---------------------------------------------------------------
# run every 10 sec for ~1 hour, then exit.
# ---------------------------------------------------------------
prev_day = datetime.datetime.now().day
n_minutes = 60
for rep in range(n_minutes):
    now = datetime.datetime.now()
    day = now.day
    fname = logdir + "/iotop%02d"%day
    if prev_day != day:
        # starting new day with a fresh file
        subprocess.call("/bin/rm -f "+fname, shell=True)
        prev_day = day
    mycmd = "sudo iotop -o -n6 -d10 -P -a -k -t -q | cut -c1-150 >>%s 2>&1" % fname
    subprocess.call(mycmd, shell=True)
    time.sleep(10)