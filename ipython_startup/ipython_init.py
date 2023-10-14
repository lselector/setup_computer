
import sys, os, re, pkgutil
import pandas as pd
import numpy as np
from numpy.random import *
pd.set_option('display.width',1000)
from mybag import *
from ipython_debug import *
import matplotlib.pyplot as plt
# --------------------------------------------------------------
def remask(ser,regex,flags=re.I):
    """
    # uses regext ocreate a mask for a DataFrame column or a series
    # Example of usage:
    #   mm=bag.member
    #   mask = remask(mm.billing_name, r'ebay')
    #   mm[['id','billing_name']][mask]
    # Noe: to make case sensitive match, provide 3rd parameter flags=0
    # for example:
    #   mask = remask(mm.billing_name, r'eBay', flags=0)
    """
    return ser.map(lambda x: True if re.search(regex, str(x), flags) else False)

# --------------------------------------------------------------
def tofile(obj,fname):
    """
    # prints any object as string to a text file
    # Example: /tofile  DF  'junk.txt'
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
def bbb():
    """
    # returns a simple pandas DataFrame - useful for drop_duplicates
    # Example of usage:
    #   bb=bbb()
    #   bb=drop_duplicates()
    """
    bb=pd.DataFrame({
        'id1':[1,2,2,3,3,3],
        'id2':[11,22,22,33,33,33],
        'val1':['v1','v2','v2','v3','v3','v3'],
        'val2':['z1','z2','z2','z3','z3','z3']})

    return bb

# --------------------------------------------------------------
def ddd(nrows=10):
    """
    # returns a simple pandas DataFrame - useful for quick tests
    # nrows is number of rows (divisible by 10), for example:
    #     df = ddd()
    #     df = ddd(100)
    #     df = ddd(10**6)   # million rows
    """
    n_aa = 10
    nn = int(nrows/n_aa)
    if nn < 1:
        nn = 1
    aa = pd.DataFrame({
          'ii':nn*[0,1,2,3,4,5,np.nan,7,8,9],
          'i1':nn*[6,5,4,3,2,1,0,-1,-2,-3],
          'i2':nn*[6,5,4,4,1,1,0,-1,-2,-3],
          'ff':nn*[0.0,1.0,2.0,np.NaN,4.0,5.0,6.0,7.0,8.0,9.0],
          'f1':nn*[0.0,1.01,2.002,3.0003,4.00004,5.000005,6.0000006,7.0,8.0,9.0],
          'f2':nn*[1.11,2.22,3.33,4.44,5.55,7.77,9.99,0.01,-0.01,-1.11],
          'ss':nn*['s0','s1','狗','汽车',np.nan,'s5','s6','s7','s8','s9'],
          's1':nn*list(np.array(['s0','s1','s2','s2',np.nan,'s5','s6','s7','s8','s9'],dtype=str)),
          's2':nn*['1.11','2.22','3.33','4.44','5.55','7.77','9.99','0.01','-0.01','-1.11'],
          'bb':nn*[True, False, True, False, np.nan, False, True,np.nan, False, True],
          'b1':nn*[True, False, True, False, True, False, True, True, False, True],
          'xx':nn*list(range(n_aa)),
          'yy':nn*[x*50 + 60 + np.random.randn() for x in range(n_aa)]
    })
    aa = aa[['ii','i1','i2','ff','f1','f2','ss','s1','s2','bb','b1','xx','yy']].copy()
    aa.index = range(len(aa))

    if 1 <= nrows < 10:
        aa = aa[:nrows+1]

    return aa

# --------------------------------------------------------------
def ddd2():
    """
    # returns a simple pandas DataFrame useful for quick stack/unstack/pivot tests
    # example of usage:
    # xx=ddd2()
    # xx.set_index(["Month","name"]).stack().unstack('Month')
    """
    aa = pd.DataFrame([
        ["Jan","name1",1,2,3],
        ["Jan","name2",4,5,6],
        ["Mar","name1",11,12,13],
        ["Mar","name2",14,15,16]],columns=["Month","name","c1","c2","c3"])

    return aa

# --------------------------------------------------------------
def ddd3():
    """
    # returns a simple pandas DataFrame useful for quick stack/unstack/pivot tests
    # example of usage:
    # xx=ddd3()
    # xx.pivot('foo','bar','baz')
    #         A   B   C
    #    one  1   2   3
    #    two  4   5   6
    #
    # xx.pivot('foo', 'bar')['baz']
    #         A   B   C
    #    one  1   2   3
    #    two  4   5   6
    """
    aa = pd.DataFrame({
      'foo':3*['one'] + 3*['two'],
      'bar':2*['A','B','C'],
      'baz':[1,2,3,4,5,6] })

    return aa[['foo','bar','baz']]

# --------------------------------------------------------------
def myprint(df):
    """
    # prints DataFrame or Series
    # Example: /myprint DF
    # notice leading "/" to tell ipython that this is a function call
    """
    print(df.to_string())

# --------------------------------------------------------------
def mygrep(df,ss):
    """
    # prints DataFrame or Series for some pattern. Returns a list of lines.
    # Example: /mygrep   DF    r'some regex'
    # notice leading "/" to tell ipython that this is a function call
    """
    lines = df.to_string().split("\n")
    return [line for line in lines if re.search(ss,line)]

# --------------------------------------------------------------
def mymodules():
    return sorted([m[1] for m in pkgutil.iter_modules()])

# --------------------------------------------------------------
def show_duplicates(df, cols=[], include_nulls=True):
    """
    # accepts a dataframe df and a column (or list of columns)
    # if list of columns is not provided - uses all df columns
    # returns a dataframe consisting of rows of df
    # which have duplicate values in "cols"
    # sorted by "cols" so that duplciates are next to each other
    # Note - doesn't change index values of rows
    """
    # ---------------------------------
    aa = df.copy()
    mycols = cols
    # ---------------------------------
    if len(mycols) <= 0:
        mycols = aa.columns.tolist()
    elif type(mycols) != list:
        mycols = list(mycols)
    # ---------------------------------
    if not include_nulls:
        mask = False
        for mycol in mycols:
            mask = mask | (aa[mycol] != aa[mycol])  # test for null values
        aa = aa[~mask]                              # remove rows with nulls in mycols
    if len(aa) <= 0:
        return aa[:0]
    # ---------------------------------
    # duplicated() method returns Boolean Series denoting duplicate rows
    mask = aa.duplicated(cols=mycols, take_last=False).values \
         | aa.duplicated(cols=mycols, take_last=True).values
    aa = aa[mask]
    if len(aa) <= 0:
        return aa[:0]
    # ---------------------------------
    # sorting to keep duplicates together
    # Attention - can not sort by nulls
    # bb contains mycols except for cols which are completely nulls
    bb = aa[mycols]
    bb = bb.dropna(how='all',axis=1)
    # sort aa by columns in bb (thus avoiding nulls)
    aa = aa.sort_index(by=bb.columns.tolist())
    # ---------------------------------
    # sorting skips nulls thus messing up the order. 
    # Let's put nulls at the end
    mask = False
    for mycol in mycols:
        mask = mask | (aa[mycol] != aa[mycol])  # test for null values
    aa1 = aa[~mask]
    aa2 = aa[mask]
    aa = aa1.append(aa2)

    return aa

# --------------------------------------------------------------
def rows_with_nulls(df):
    """
    # accepts a DataFrame with 0 or more rows
    # returns a DataFrame which contains rows with at least one null value.
    # If no nulls - returns an empty DataFrame
    """
    mask=False
    for col in df.columns: mask = mask | df[col].isnull()
    return df[mask]

# --------------------------------------------------------------
def df_size(df):
    """
    # ballpark estimate of DataFrame memory usage
    """
    mysizes = {
        float : sys.getsizeof(1.0),
        int   : sys.getsizeof(1),
        bool  : sys.getsizeof(True),
    }
    bb = df.dtypes.tolist()
    memsize = 0
    for mytype in bb:
        if mytype == float:
            memsize += mysizes[float]
        elif mytype == int:
            memsize += mysizes[int]
        elif mytype == bool:
            memsize += mysizes[bool]
        else:
            memsize += 30

    return memsize * len(df)

# --------------------------------------------------------------
def myhist(N=30, regex='', pr=True):
    """
    # ipython history function searches multiple sessions.
    # You can specify number of lines to search, and optionally regex to select from these commands.
    #     myhist(200)
    #     myhist(1000, 'myword')
    # You can return history list into a variable instead of printing:
    #     aa = myhist(10000, 'cpx', pr=False)
    # Note: alternative approach to this function is to create a magic function
    # See how to do it here:
    # http://ipython.org/ipython-doc/stable/interactive/reference.html
    # Also you can create an ipython function which would use this ipython magic
    # command to output history from a range of sessions:
    #    ~2000/1-~0/2000
    """
    import subprocess
    import re
    # make a copy of the database to query it (to avoid locking)
    mydb = '~/.ipython/profile_default/history.sqlite'
    mydb2 = mydb + ".tmp"
    cmd1 = "/bin/cp -f %s %s" % (mydb, mydb2)
    _ = subprocess.check_output(cmd1, shell=True)

    cmd2 = 'sqlite3 %s "select source_raw from history"' % mydb2
    txt = subprocess.check_output(cmd2, shell=True)
    txt = txt.decode("utf-8")
    lines = txt.split('\n')
    lines2 = []
    if len(regex) <= 0:
        lines2 = lines[-N:]
    else:
        for line in lines:
            if re.search(regex, line, re.I):
                lines2.append(line)
        lines2 = lines2[-N:]
    if pr:
        for line in lines2:
            print(line)
    else:
        return lines2

# --------------------------------------------------------------
def read_pk(fname):
    import pickle
    return pickle.load(open(fname, "rb"))

# ##############################################################
# main execution
# ##############################################################

