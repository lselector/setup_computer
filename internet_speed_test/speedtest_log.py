
# --------------------------------------------------------------
# speedtest_log.py - by Lev Selector
# Utility to monitor internet speed on a Mac.
# Every 10 min refreshes image $HOME/internet_speed_test/sptest.png
# 
# 
# To make it work:
#   create directory $HOME/internet_speed_test/
#   and copy there the following files:
#      speedtest.py
#      log_speedtest.py
#      speedtest.log
#      speedtest.ipynb
# 
# cd ~/Desktop
# ln -s /Users/levselector/internet_speed_test/sptest.png sptest.png

# Note: the jupyter notebook helps to debug code
# (in case some libraries are missing).
#
# Then add the following entry to the crontab:
# 
# # run internet speed test every 10 min
# */10 * * * * bash -c 'cd ~/; source .bashrc; cd ~/internet_speed_test; python speedtest_log.py >> speedtest.err 2>&1'
# 
# 
# Note - the original code:
#     https://www.accelebrate.com/blog/pandas-bandwidth-python-tutorial-plotting-results-internet-speed-tests/
#     https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
# 
# See there how to parse the log file and show graphics
# --------------------------------------------------------------
import sys, os
import logging, datetime
import matplotlib.pyplot as plt
from matplotlib import dates, rcParams
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

SPEEDTEST_CMD = './speedtest.py'
LOG_FILE      = 'speedtest.log'
ERR_FILE      = 'speedtest.err'
IMG_FILE      = os.getenv('HOME') + '/internet_speed_test/sptest.png'

# --------------------------------------------------------------
def setup_logging():
    logging.basicConfig (
        filename = LOG_FILE,
        level    = logging.INFO,
        format   = "%(asctime)s %(message)s",
        datefmt  = "%Y-%m-%d %H:%M" )

# --------------------------------------------------------------
def get_speedtest_results():
    """
    # Run test and parse results.
    # Returns tuple of ping speed, download speed, and upload speed,
    # or raises ValueError if unable to parse data.
    """
    ping = download = upload = None

    with os.popen(SPEEDTEST_CMD + ' --simple') as speedtest_output:
        for line in speedtest_output:
            label, value, unit = line.split()
            if 'Ping' in label:
              ping = float(value)
            elif 'Download' in label:
              download = float(value)
            elif 'Upload' in label:
              upload = float(value)

        if all((ping, download, upload)): # if all 3 values were parsed
          return ping, download, upload
        else:
          raise ValueError('TEST FAILED')

# --------------------------------------------------------------
def make_plot(plt, df, row_index=1, nhours=2):
    # ---------------------------------
    # select last "nhours" of data
    index_max = df.index[-1]
    dtmax = df.loc[index_max,'timestamp']
    dtmin = dtmax - datetime.timedelta(hours=nhours)

    mask = df['timestamp'] > dtmin
    df = df.loc[mask,:].copy()
    df.index = range(len(df))
    # ---------------------------------
    # subplot(nrows, ncols, index, **kwargs)
    plt.subplot(3, 1, row_index)
    plt.plot(df['timestamp'],df['download'], 'b-')
    plt.title('Internet Download Speed in Mbs (Megabits per second) : 240 Mbs = 30 MBytes/s')
    plt.ylabel('Megabits / sec')
    y_range = 1.2*df.download.max()
    plt.ylim(0.0,y_range)
    plt.xlabel('Date/Time')
    plt.xticks(rotation=45, ha='right')
    # ---------------------------------
    ax = plt.gca()    # get current Axes instance
    fg = plt.gcf()    # get current figure

    start = df.loc[0,'timestamp']
    end   = df.loc[df.index[-1],'timestamp']
    delta = (end-start)/11.0
    arr_ts = [start]
    for ii in range(12):
        val = arr_ts[-1]       # last element
        arr_ts += [val+delta]  # add shifted by delta

    ax.xaxis.set_ticks(arr_ts)
    h_fmt = dates.DateFormatter('%m/%d %H:%M')
    ax.xaxis.set_major_formatter(h_fmt)
    # ---------------------------------
    ax.xaxis.set_tick_params(labelsize=9)
    ax.yaxis.set_tick_params(labelsize=9)

    fg.subplots_adjust(bottom=.25)
    plt.grid();

# --------------------------------------------------------------
def read_data():
    df = pd.io.parsers.read_csv(
        'speedtest.log',
        names='date time ping download upload'.split(),
        header=None,
        sep=r'\s+',
        parse_dates={'timestamp':[0,1]},
        na_values=['TEST','FAILED'])

    for col in 'ping download upload'.split():
        df[col] = df[col].fillna(0.0)

    # We run script every 10 min, or 6/hr, or 6*24=144/day
    Nrows = 5*144   # 720 rows
    return df[-Nrows:]   # return dots for last Nrows only

# --------------------------------------------------------------
def main():
    setup_logging()
    # ------------------------------------------
    # run speed test - and write row into LOG_FILE
    try:
        ping, download, upload = get_speedtest_results()
    except ValueError as err:
        logging.info(err)
    else:
        logging.info("%5.1f %5.1f %5.1f", ping, download, upload)

    # ------------------------------------------
    # shorten the log file - keep only last 2,000 rows
    MYCMD = f"""echo "$(tail -2000 {LOG_FILE})" > {LOG_FILE}"""
    os.system(MYCMD)
    # shorten the err file - keep only last 2,000 rows
    MYCMD = f"""echo "$(tail -2000 {ERR_FILE})" > {ERR_FILE}"""
    os.system(MYCMD)

    # ------------------------------------------
    # read last 720 rows
    df = read_data()   # pandas DataFrame with up to 720 rows
    
    # ------------------------------------------
    # make a graph with two plots - and save as IMG_FILE
    fig_width  = 10
    fig_height = 5
    rcParams['figure.figsize'] = fig_width, fig_height
    plt.gcf().clear()
    make_plot(plt, df.copy(), row_index=1, nhours=5*24)
    make_plot(plt, df.copy(), row_index=3, nhours=2   )
    fg = plt.gcf()
    fg.savefig(IMG_FILE)

# --------------------------------------------------------------
if __name__ == '__main__':
  main()

