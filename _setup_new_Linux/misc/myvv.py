"""
# myvv.py - script to show server status
# Invoke it via "vv" alias
# Usage:
#     vv           # look at last 24 hrs of log files
#     vv 48        # look at last 48 hours
#     vv 48 24     # look at hours [-48, -24) (skip very last 24 hrs)
#
# by Lev Selector, 2021, 2022
"""

import os, sys, time, subprocess
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
from myutil import *
from myutil_dt import *

# ---------------------------------------------------------------
def process_cmd_args(bag):
    """
    # processes cmd arguments - and populates bag.arg_*
    # we have only one positional argument - number of hours
    # by default it is 24
    """
    descr_str = """script to show status of jobs on server for the last 24 or more hours"""
    bag.app.parser = argparse.ArgumentParser(description=descr_str)
    bag.app.parser.add_argument('arg_hours',      nargs='?', default=24, help='number of hours to go back')
    bag.app.parser.add_argument('arg_hours_skip', nargs='?', default= 0, help='number of recent hours to skip')

    parsed, unknown = bag.app.parser.parse_known_args()
    if len(unknown):
        exit_with_error(bag, "unrecognized argument(s) " + str(unknown))

    bag.arg_hours = 24
    bag.arg_hours_skip = 0

    if parsed.arg_hours:
        bag.arg_hours = int(float(parsed.arg_hours))

    if parsed.arg_hours_skip:
        bag.arg_hours_skip = int(float(parsed.arg_hours_skip))

    if bag.arg_hours_skip >= bag.arg_hours:
        bag.arg_hours_skip = bag.arg_hours

    bag.arg_mins  = bag.arg_hours * 60
    bag.arg_mins_skip  = bag.arg_hours_skip * 60

    print(f"processing logs for {bag.arg_hours} hours")
    if bag.arg_hours_skip > 0 :
        print(f"skipping last {bag.arg_hours_skip} hours")

# ---------------------------------------------------------------
def myrun0(cmd):
    """ simple function to run shell command and return a string """
    try:
        txt = subprocess.check_output(cmd, shell=True).decode().strip()
        return txt
    except subprocess.CalledProcessError as myerr:
        # print("vv error code  :", myerr.returncode)
        # print("vv error output:", myerr.output)
        return ""

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
def get_logs_with_QUERIES_FINISHED_OK(bag):
    """
    # looks for log file containing QUERIES_FINISHED_OK
    # strips dates, removes duplicates
    # and writes a list of unique "beginnings" of
    # those log files into the file:
    #   /data/code/misc/logs_QUERIES_FINISHED_OK_auto.txt
    """
    # ---------------------------------
    cmd  = f"grep -l QUERIES_FINISHED_OK /data/log/*log | grep -v frappe | sort | uniq"
    myfiles = myrun(cmd)
    mylist = myfiles.strip().split("\n")
    # print(mylist)
    for ii in range(len(mylist)):
        name = mylist[ii]
        name = name.replace('/data/log/','')
        name = re.sub(r'\d{8}_\d{6}.*log','',name)
        name = re.sub(r'_$','',name)
        mylist[ii] = name
    mylist = sorted(set(mylist))
    myfile = "/data/code/misc/logs_QUERIES_FINISHED_OK_auto.txt"
    fh = open(myfile,"w")
    for fname in mylist:
        fh.write(fname+"\n")
    fh.close()

# ---------------------------------------------------------------
def read_words(fname):
    """
    # accepts a name of a text file with lists of words
    # identifying "beginnings" of log files
    # one per line
    # removes comments and extra spaces and ending underscores
    # returns a list of cleaned words (or empty list)
    """
    if not os.path.exists(fname):
        return []
    fh = open(fname,"r")
    words = fh.read().strip().split("\n")
    words = [x.strip() for x in words]
    words2 = []
    for name in words:
        if len(name) <=0:
            continue
        if name[0] == '#':
            continue
        name = re.sub(r'_+$','',name)
        words2.append(name)

    return words2

# ---------------------------------------------------------------
def get_exceptions(bag):
    """
    # read two files containing beginnings of log files
    # creates two sets - and subtracts them
    # convert to list - and saves to bag.exceptions
    """
    get_logs_with_QUERIES_FINISHED_OK(bag)
    list1 = read_words("/data/code/misc/logs_QUERIES_FINISHED_OK_auto.txt")
    list2 = read_words("/data/code/misc/logs_QUERIES_FINISHED_OK_delete.txt")
    mylist = sorted( set(list1) - set(list2))
    bag.exceptions = mylist

# ---------------------------------------------------------------
def get_list_of_log_files(bag):
    """
    # get list of recent logs
    # show number of errors in them
    """
    print("-"*50, "errors recent")
    # ---------------------------------
    # get a list of recent log files
    cmd  = f"/usr/bin/find /data/log/ -mmin -{bag.arg_mins} -mmin +{bag.arg_mins_skip}"
    cmd += f" -type f -print  "

    myfiles_new = myrun(cmd)
    myfiles_new_list = myfiles_new.strip().split("\n")
    bag.myfiles_new      = myfiles_new                   # newline separated
    bag.myfiles_new_list = myfiles_new_list              # list
    bag.myfiles_new_sp   = ' '.join(myfiles_new_list)    # space-separated
    # ---------------------------------
    # get number of errors
    cmd  = f"cat {bag.myfiles_new_sp} | grep -i 'Traceback\|fatal\|error' "
    cmd += f" | grep -v 'Completed - ' | grep -v 'labels, errors=errors' | wc -l "

    mynum_new = myrun(cmd)
    bag.mynum_new = mynum_new
    ss  = f"Found {mynum_new} errors in last-day logs under /data/log/ "
    ss += f" (some of them usually get corrected via re-try)"
    print(ss)

# ---------------------------------------------------------------
def show_errors_in_normal_logs(bag):
    """ show errors in normal logs """
    print("-"*50, "errors")
    cmd  = f"grep -i 'Traceback\|fatal\|error' {bag.myfiles_new_sp} "
    cmd += f" | grep -v {bag.except_str} "
    cmd += f" | grep -v 'Completed - ' "
    cmd += f" | grep -v 'labels, errors=errors' "
    cmd += f" | grep -i 'Traceback\|fatal\|error';"
    # print("running cmd:", cmd,"\n")
    txt = myrun(cmd)
    print(txt)

# ---------------------------------------------------------------
def get_err_lst_from_txt(txt):
    """
    # called from show_errors_in_special_files()
    # receives a multiline string
    # splits it into Lines
    # returns list of lines with errors (or empty list)
    """
    myout = []
    mylist = txt.strip().split("\n")
    for ss in mylist:
        if not re.findall(r'Traceback|fatal|error',ss,re.IGNORECASE):
            continue
        if 'Completed - ' in ss:
            continue
        if 'labels, errors=errors' in ss:
            continue
        myout.append(ss)
    return myout

# ---------------------------------------------------------------
def show_errors_in_special_files(bag):
    """
    # processes logs which may have QUERIES_FINISHED_OK in them
    # ( listed in bag.exceptions )
    """
    print("-"*50, "errors in 'special' logs")

    for myname in bag.exceptions:
        cmd  = f"/usr/bin/find /data/log/ -mmin -{bag.arg_mins} -mmin +{bag.arg_mins_skip} -type f "
        cmd += f" -name '*{myname}*' -print  | grep -v frappe "
        myfiles_new = myrun(cmd)

        myfiles_new_list = myfiles_new.strip().split("\n")
        # keep only non-empty
        myfiles_new_list = [i.strip() for i in myfiles_new_list if len(i.strip())]
        if len(myfiles_new_list) == 0:
            continue

        for myfile in myfiles_new_list:
            txt = ""
            with open(myfile,'r') as fh:
                txt = fh.read()
            parts_lst = txt.split("QUERIES_FINISHED_OK")
            errs = [get_err_lst_from_txt(xx) for xx in parts_lst]

            # ----- QUERIES_FINISHED_OK worked
            if (
                    (len(errs) == 2) and ("litig_dash" not in myfile)
                    or
                    ( ("litig_dash" in myfile) and (len(errs) == 5) )
                ):  # show errors in last part only
                xx = errs[-1]
                if len(xx) > 0:
                    for ss in xx:
                        print(myfile,":", ss)

            # ----- no or not enough QUERIES_FINISHED_OK
            elif (
                    (len(errs) == 1)
                    or
                    ( ("litig_dash" in myfile) and (len(errs) < 5) )
                 ):  # show all errors
                for xx in errs:
                    if len(xx) > 0:
                        for ss in xx:
                            print(myfile,":", ss)

# ---------------------------------------------------------------
def num_errors_in_old_logs(bag):
    """ prints number of errors in old logs only """
    print("-"*50,"errors in old logs")
    # ---------------------------------
    # get a list of old log files
    #    myfiles_old=`/usr/bin/find /data/log/ -mmin +"$mymin" -type f -print`;
    cmd  = f"/usr/bin/find /data/log/ -mmin +{bag.arg_mins} -mmin +{bag.arg_mins_skip} "
    cmd += f" -type f -print | grep -v frappe "
    myfiles_old = myrun(cmd)

    myfiles_old_list = myfiles_old.strip().split("\n")
    myfiles_old_sp   = ' '.join(myfiles_old_list)    # space-separated
    # ---------------------------------
    # get number of errors
    cmd  = f"cat {myfiles_old_sp} | grep -i 'Traceback\|fatal\|error' "
    cmd += f" | grep -v 'Completed - ' | grep -v 'labels, errors=errors' | wc -l "
    mynum_old = myrun(cmd)

    print(f"Found {mynum_old} errors in older logs under /data/log/")

# ---------------------------------------------------------------
def show_warnings(bag):
    """ show warnings in new log files """
    print("-"*50, "warnings")
    # cmd = f"cat {bag.myfiles_new_sp} | grep -i 'WFM Data' | wc -l"
    cmd = f"cat {bag.myfiles_new_sp} | grep -i 'warning' | grep -v omsagent | grep -v frappe | wc -l"
    mynum_new = myrun(cmd)
    print(f"Found {mynum_new} warnings in last-day logs under /data/log/")
    #    cmd = f"grep -i 'WFM Data' {bag.myfiles_new_sp}"
    #    cmd = f"grep -i 'warning' {bag.myfiles_new_sp}"
    #    cmd = f"grep -i 'warning' {bag.myfiles_new_sp} | grep -v 'DeprecationWarning' "
    cmd = f"grep -i 'warning' {bag.myfiles_new_sp} | grep -Pv 'omsagent' | grep -v frappe "
    txt = myrun(cmd)
    if len(txt):
        print(txt)

# ---------------------------------------------------------------
def show_recent_logs(bag):
    """ show recent logs"""
    print("-"*50,"recent logs")
    print("last-day logs (time in UTC) :")
    cmd  = f"/usr/bin/find /data/log/ -mmin -{bag.arg_mins} -mmin +{bag.arg_mins_skip} -type f "
    cmd += f" -ls | grep -v frappe | sort -k 11"
    txt = myrun(cmd)
    print(txt)

# ---------------------------------------------------------------
def numbers_dirs_jobs_scripts(bag):
    """ prints numbers of dirs, crons, shell and python scripts """
    print("-"*50)
    cmd = f"/bin/ls -d /data/code/*/ | grep -v BACKUPS | wc -l"
    num_dirs = myrun(cmd)
    # ---------------------------------
    cmd = f"crontab -l | grep -E '^@|^\*|^[0-9]' | wc -l"
    num_cron = myrun(cmd)
    # ---------------------------------
    cmd = f"/usr/bin/fd -e py . /data/code | wc -l"
    num_py = myrun(cmd)
    # ---------------------------------
    cmd = f"/usr/bin/fd -e sh -e bash . /data/code | wc -l"
    num_sh = myrun(cmd)
    # ---------------------------------
    print(f"Total: {num_dirs} code dirs, {num_cron} cron jobs, {num_sh} shell scripts, {num_py} python scripts")

# ---------------------------------------------------------------
def our_web_processes(bag):
    """ print numbers of web-service related processes """
    print("-"*50)
    # mylist = ['gunicorn_test',
    #           'gunicorn_prod',
    #           'nginx']
    mylist = ['nginx']
    for myvar in mylist:
        cmd = f"ps auxww | grep {myvar} | grep -v grep | wc -l"
        mynum = myrun(cmd)
        print(f"{mynum:>2s} {myvar} processes running")

# ---------------------------------------------------------------
def our_crontab_jobs(bag):
    """ show active crontab jobs """
    print("-"*50, "crontab processes")
    # ---------------------------------
    cmd = "date"
    mydate = myrun(cmd)
    # ---------------------------------
    cmd = f"ps auxww | grep crontab | grep -v grep | wc -l"
    mynum = myrun(cmd)
    mynum = int(float(mynum))
    if mynum <= 0:
        # print(f"{mynum} crontab processes running")
        return
    print(f"{mynum} crontab processes running at: {mydate}")
    cmd = "ps -eo user,pid,ppid,lstart,etime,args | head -1"
    txt = myrun(cmd)
    print(txt)
    cmd = "ps -eo user,pid,ppid,lstart,etime,args | grep crontab | grep -v grep"
    txt = myrun(cmd)
    print(txt)

# ---------------------------------------------------------------
def our_processes(bag):
    """ show our non crontab and non web processes """
    print("-"*50, "other processes")
    cmd = "ps -eo user,pid,ppid,lstart,etime,args --sort start_time | grep -v grep"
    run_all = myrun(cmd)
    run_all_lst = run_all.split("\n")
    run_all_lst = [i.strip() for i in run_all_lst if len(i.strip())]
    # ---------------------------------
    # lines look like this:
    # root     21342     2 Sat Jun 26 22:28:49 2021       07:26 [kworker/0:0-cgr]
    #
    # the date is in parts 4,5,6 : Sat Jun 26
    # ---------------------------------
    # get startdate in format Sun Jun  6
    startdate = ""
    for elem in run_all_lst:
        if re.search(r'/lib/systemd/systemd-journald', elem):
            parts = elem.split()
            dw, mo, dm = parts[3:6]
            startdate = f"{dw} {mo} {dm:>2s}"
            break
    # ---------------------------------
    cmd  = f"ps -eo user,pid,ppid,lstart,etime,args --sort start_time "
    cmd += f" | grep -Pv '^(root|systemd+|syslog|message+|daemon|www\-data|postfix)' "
    cmd += f" | grep -v '{startdate}' " # exclude commands on startdate
    cmd += f" | grep -Pv 'main;main|gunicorn|grep|sshd|myvv.py|\-bash' "
    cmd += f" | grep -v 'ps -eo' "
    cmd += f" | grep -v 'omsagent' "
    cmd += f" | grep -v '/opt/omi/' "
    cmd += f" | grep -v '/usr/sbin/uuidd' "
    cmd += f" | grep -v '/lib/systemd/systemd' "
    cmd += f" | grep -v '(sd-pam)' "
    cmd += f" | grep -Pv 'honcho|bench|frappe|redis|yarn|esbuild' "
    run_lst = myrun(cmd).split("\n")
    run_lst = [i.strip() for i in run_lst if len(i.strip())]
    run_lst = [i for i in run_lst if not re.findall(r'STARTED|crontab',i)]
    mynum = len(run_lst)
    if mynum > 0:
        print(f" {mynum} our processes running:")
        cmd = "ps -eo user,pid,ppid,lstart,etime,args | head -1"
        txt = myrun(cmd)
        print(txt)
        for elem in run_lst:
            print(elem)

# ---------------------------------------------------------------
def memory_usage_from_top(bag):
    print("-"*50, "memory usage")
    cmd = "free -h"
    txt = myrun(cmd)
    lines = txt.split("\n")
    lines[0] = "-"*10 +" " + lines[0]
    for ss in lines:
        words = [f"{x:10s}" for x in ss.split()]
        line = " ".join(words)
        print(line)
#    print(txt)

# ---------------------------------------------------------------
def memory_RES_hogs(bag):
    """ show our largest memory apps currently running """
    print("-"*50, "memory (RES) hogs")
    cmd = "top -b -n 1 -o +RES -c | /bin/grep -vP 'gunicorn|\broot\b' | head -n 14 | tail -n 8"
    txt = myrun(cmd)
    print(txt)

# ---------------------------------------------------------------
def disc_usage(bag):
    """ shows used and available disk space for HOME and /data """
    print("-"*50, "disk usage")
    cmd = "df -h ~ /data"
    txt = myrun(cmd)
    print(txt)

# ---------------------------------------------------------------
def main(bag):
    """
    # main execution
    """
    # mylog(bag, "in main")

    # bag.exceptions = special logs for scripts which print "QUERIES_FINISHED_OK"
    get_exceptions(bag)
    bag.except_str = "'" + '\\|'.join(bag.exceptions) + "'"
    process_cmd_args(bag)

    show_recent_logs(bag)
    get_list_of_log_files(bag)
    show_errors_in_normal_logs(bag)
    show_errors_in_special_files(bag)
    num_errors_in_old_logs(bag)
    show_warnings(bag)
    numbers_dirs_jobs_scripts(bag)
    our_web_processes(bag)
    our_crontab_jobs(bag)
    our_processes(bag)
    memory_usage_from_top(bag)
    # memory_RES_hogs(bag)
    disc_usage(bag)
    print("-"*50)

# ---------------------------------------------------------------
# main execution
# ---------------------------------------------------------------
if __name__ == "__main__":
    bag  = MyBunch()
    bag.mask_log_str = ""
    myinit(bag)
    main(bag)

