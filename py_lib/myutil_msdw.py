
"""
# utility functions to work with MSDW (MicroSoft Data Warehouse)
# (also known as Azure SQL Data Warehouse)
#
# The connection info comes from env variable $MSDW
#
# main functions:
#     db_conn_open(bag)
#     db_conn_close(bag)
#     do_query(bag,sql)   # select ...
#     do_sql(bag,sql)     # create, drop, insert, update, delete, etc.)
#
# typical usage
#     import myutil_msdw
#     from myutil_msdw import *
#     bag=MyBunch()
#     db_conn_open(bag)
#     err_str = do_sql(bag,sql=sql1)
#     df,err_str = do_query(bag,sql2)
#     db_conn_close(bag)
"""

import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
import sys

import pyodbc
import pandas.io.sql as psql
import time

import myutil
from myutil import *
import myutil_dt
from myutil_dt import *

from ipython_debug import *

# ---------------------------------------------------------------
def df_cols_lower(df):
    """
    # accepts and returns a dataframe
    # converts column names to lower case
    """
    cols = df.columns
    cols_lower = [xx.lower() for xx in cols]
    mydict = dict(zip(cols, cols_lower))
    df = df.rename(columns = mydict, copy=False)
    return df

# --------------------------------------------------------------
def form_conect_str():
    """
    # creates pyodbc conection string for Azure Data Warehouse
    # from env variable MSDW
    # which has structure: 
    # "-S myserver -U myuser -P mypassword -d mydb"
    # returns string in format:
    # "DRIVER=_;SERVER=_;PORT=1433;DATABASE=_;UID=_;PWD=_"
    # returns two strings: normal and with masked password
    """
    mm = os.getenv("MSDW").split()
    # print(mm)
    if not ( (len(mm)==8) and (mm[0]=='-S') and (mm[2]=='-U') 
             and (mm[4]=='-P') and (mm[6]=='-d') ):
        ss = "ERROR - MSDW env. variable should have 8 elements: "
        ss += " -S myserver -U myuser -P mypassword -d mydb"
        print(ss)
        sys.exit(1)

    drv ='{ODBC Driver 17 for SQL Server}'
    srv = mm[1]
    usr = mm[3]
    psw = mm[5]
    db  = mm[7]
    ss1 = "DRIVER=%s;SERVER=%s;PORT=1433;DATABASE=%s;UID=%s;PWD=%s" \
         % (drv,srv,db,usr,psw)
    ss2 = "DRIVER=%s;SERVER=%s;PORT=1433;DATABASE=%s;UID=%s;PWD=%s" \
         % (drv,srv,db,usr,"__hidden__")

    return ss1,ss2

# --------------------------------------------------------------
def str_for_printing(mystr, prefix):
    """
    # add prefix to every line of a myltiline string
    """
    mystr = str(mystr)
    mylist = mystr.split("\n")
    pr_str = ""
    for ss in mylist:
        pr_str += prefix + " " + ss + "\n"
    return pr_str

# --------------------------------------------------------------
def db_conn_open(bag):
    """
    # connects to database
    # doesn't check if connection already exists
    # just tries to create a new one
    # stores connection as bag.cnxn
    # should never stop on failure
    # returns True on success, False on Failure
    """
    try:
        ss1,ss2 = form_conect_str()
        #print(ss1)                # real conn. string
        print("Connecting: ", ss2) # string with hidden password
        cnxn = pyodbc.connect(ss1) # real conn. string
        bag.cnxn = cnxn
        return True
    except:
        print("ERROR in db_conn_open() - can't open DB connection")
        if test_avail(bag, "cnxn"):
            del bag["cnxn"]
        return False

# --------------------------------------------------------------
def close_cursor(bag):
    """
    # closes and deletes bag.cursor
    # should never stop on failure
    # doesn't return anything
    """
    if test_avail(bag, "cursor"):
        try:
            bag.cursor.close()
        except:
            pass
        del bag.cursor

# --------------------------------------------------------------
def db_conn_close(bag):
    """
    # closes database connection bag.cnxn
    # should never stop on failure
    # doesn't return anything
    """
    if not test_avail(bag, "cnxn"):
        return
    close_cursor(bag)

    try:
        if bag.cnxn != None:
            bag.cnxn.close()
    except:
        pass

    del bag.cnxn

# --------------------------------------------------------------
def test_connection(bag):
    """
    # checks bag.cnxn & bag.cursor
    # reconnects/reopens as needed
    # should never stop on failure
    # returns True on success, False on failure
    """
    close_cursor(bag)
    if not test_avail(bag, "cnxn"):
        db_conn_open(bag)
    if not test_avail(bag, "cnxn"):
        mylog(bag, "ERROR in test_connection(), can't connect to database")
        return False
    # If we are here - we have connection bag.cnxn
    sql = "select 1 as 'aa'"
    try:
        df = psql.read_sql(sql, bag.cnxn)
        return True
    except:
        mylog(bag, "ERROR in test_connection(), can't test SQL query")
        return False

# --------------------------------------------------------------
def do_query(bag, sql='',stop_on_error=True):
    """
    # run query, returns a tuple (df, err)
    # where df - Pandas DataFrame
    #       err - error string (empty if success)
    """
    mylog(bag, "about to run SQL:\n\n" + sql + "\n\n")
    df    = DataFrame()
    err_str = "ERROR in myutil_msdw.do_query()"

    if not test_connection(bag):
        mylog(bag, err_str)
        if stop_on_error:
            sys.exit(1)
        return df,err_str

    t_start = time.time()
    try:
        df = psql.read_sql(sql, bag.cnxn)
        err_str = ""
    except Exception as DatabaseError:
        DatabaseError  = str(DatabaseError).strip()
        mylog_err(bag, err_str)
        mylog_err(bag, DatabaseError)
        if stop_on_error:
            runtime_str = str( round(time.time() - t_start,2) )
            mylog_err(bag, "query runtime was %s sec\n" % runtime_str)
            sys.exit(1)
        df = DataFrame()
        err_str = DatabaseError

    runtime_str = str( round(time.time() - t_start,2) )
    mylog(bag, "query runtime was %s sec\n" % runtime_str)

    return df,err_str

# --------------------------------------------------------------
def do_sql(bag, sql='',stop_on_error=True):
    """
    # insert, update, delete, etc.
    # usage: do_sql(bag, sql)
    # returns empty string on success, error string on failure
    """
    mylog(bag, "about to run SQL:\n\n" + sql + "\n\n")
    err_str = "ERROR in myutil_msdw.do_sql()"

    if not test_connection(bag):
        mylog(bag, err_str)
        if stop_on_error:
            sys.exit(1)
        return err_str

    # ---------------------------------
    def proc_err(bag, step="", t_start="",sql=""):
        # debug_here()
        close_cursor(bag)
        err_str = "Error %s in do_sql() :\n" % step
        err_str += sql
        runtime_str = str( round(time.time() - t_start,2) )
        mylog_err(bag, "do_sql() runtime was %s sec\n" % runtime_str)
        mylog_err(bag, err_str)
        if stop_on_error:
            sys.exit(1)
        return err_str

    # ---------------------------------
    t_start = time.time()
    try:
        bag.cursor = bag.cnxn.cursor()
    except Exception:
        err_str = proc_err(bag,step="creating cursor",t_start=t_start,sql=sql)
        return err_str

    try:
        bag.cursor.execute(sql)
    except Exception:
        err_str = proc_err(bag,step="executing cursor",t_start=t_start,sql=sql)
        return err_str

    try:
        bag.cursor.commit()
    except Exception:
        err_str = proc_err(bag,step="committing cursor",t_start=t_start,sql=sql)
        return err_str

    runtime_str = str( round(time.time() - t_start,2) )
    mylog(bag, "do_sql() runtime was %s sec\n" % runtime_str)
    return ""

# --------------------------------------------------------------
# main execution portion - used for testing of this module
# --------------------------------------------------------------
if __name__ == '__main__':
    bag = MyBunch()
    test_connection(bag)

    # sql1="""insert into tab1 values ('2019-07-11', ..)"""
    # err_str = do_sql(bag, sql=sql1,stop_on_error=False)

    df,err_str = do_query(bag, sql="select count(1) from tab1",stop_on_error=False)

    print(">>>>> df=",df)

# --------------------------------------------------------------
# --------------------------------------------------------------

