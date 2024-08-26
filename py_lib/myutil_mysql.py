
"""
# myutil_mysql.py
#
# There are multiple modules to work with MySQL
#  - https://pynative.com/python-mysql-database-connection/
#      -  MySQL Connector Python
#      -  PyMySQL
#      -  MySQLDB
#      -  MySqlClient
#      -  OurSQL
#
# This file uses "MySQL Connector Python" because:
#   - it is written in pure Python
#   - it is an official Oracle-supported driver
#   - it is actively maintained
#
# It can be installed via:
#   pip install mysql-connector-python
#
# - https://dev.mysql.com/doc/connector-python/en/
# - https://pypi.org/project/mysql-connector-python/
#
# Examples of usage:
# - https://dev.mysql.com/doc/connector-python/en/connector-python-examples.html
# - https://medium.com/analytics-vidhya/importing-data-from-a-mysql-database-into-pandas-data-frame-a06e392d27d7
#
# pip install mysql-connector-python
#
# Then:
# 
#    import mysql.connector as connection
#    import pandas as pd
#    try:
#        dbh = connection.connect(
#            host="localhost", 
#            database = 'testdb',
#            user="root", 
#            passwd=os.getenv("MYSQL_PWD"),
#            use_pure=True)
#        sql = "select * from tab1;"
#        df = pd.read_sql(sql, dbh)
#        dbh.close() #close the connection
#    except Exception as e:
#        dbh.close()
#        print(str(e))
#
# More links:
# 
# https://www.geeksforgeeks.org/mysqldb-connection-python/
# https://pynative.com/python-mysql-database-connection/
# https://realpython.com/python-mysql/
# https://www.dataquest.io/blog/sql-insert-tutorial/
# https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-transaction.html
# https://stackoverflow.com/questions/35641893/best-way-for-python-to-interface-with-mysql 
# https://github.com/tornadoweb/tornado/blob/branch2.4/tornado/database.py
# https://www.guru99.com/python-mysql-example.html
"""

import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
# -------------------------------------
import os, sys, time, re
import datetime as dt
import numpy as np
import pandas as pd
import mysql.connector

# --------------------------------------------------------------
def remove_extra_indents(sql):
    """
    # removes empty lines
    # adjusts left indentation
    """
    sql  = "\n\n" + sql + "\n\n"
    sql  = re.sub(r'\r','',sql)
    sql  = re.sub(r'\t','  ',sql)
    r1 = sql.split('\n')
    r2 = [] 
    indents = []
    for myrow in r1:
        ss = myrow.rstrip()
        if len(ss) > 0:
            r2.append(ss)
            indents.append(len(ss) - len(ss.lstrip()))

    if len(r2) <= 0:
        return ''

    ind_min = min(indents)
    sql_new = '\n'
    ind_new = ' '*4
    for myrow in r2:
        sql_new += ind_new + myrow[ind_min:] + "\n"

    return sql_new + "\n"

# --------------------------------------------------------------
def dbquote(form, val):
    """
    # accepts a format string (%s, %d, or %f) and a value
    # formats are required for this code to work (form can not be empty).
    # returns string in double-quotes.
    # internal double-quotes (if any) are "escaped" by repeating them twice
    """
    if (not form) or ('s' in form):
    # will actually fail on empty format - so that you can fix your code
        ss = (form % val).strip()
        return '"' + ss.replace('"','""') + '"'   # duplicate double-quotes (if any)
    else:
        return (form % val).strip()

# --------------------------------------------------------------
def connect_to_mysql(myuser=None, mypasswd=None):
    """
    # connects to hard-coded MySQL database
    # returns tuple (cnx, err_code)
    # where 
    #     cnx - connection object 
    #     err_code = 0 on success, something else on error
    """
    try:
        cnx = mysql.connector.connect(
            host="localhost", 
            database = 'testdb',
            user=myuser, 
            passwd=mypasswd,
            use_pure=True)
        return cnx, 0
    except Exception as e:
        print(str(e))
        return None, str(e)

# --------------------------------------------------------------
def do_query(cnx, sql):
    """
    # runs query
    # returns tuple (df,err_code)
    # where 
    #     df - pandas DataFrame, 
    #     err_code = 0 on success, something else on error
    """
    try:
        df = pd.read_sql(sql, cnx)
        return df, 0
    except Exception as e:
        print(str(e))
        return pd.DataFrame(), str(e)

# --------------------------------------------------------------
def do_sql(cnx, sql):
    """
    # runs sql to insert, update, delete, create, drop, alter, etc.
    # returns err_code = 0 on success, something else on error
    """
    try:
        cursor = cnx.cursor()
        cursor.execute(sql)
        cnx.commit()
        cursor.close()
        return 0
    except Exception as e:
        print(str(e))
        return str(e)

# --------------------------------------------------------------
if __name__ == "__main__":

    cnx,err = connect_to_mysql()

    sql1 = "select * from test1"

    val = 5
    sql2 = f"""
        insert into test1 
        values ({val},'Moscow')
        """
    sql2 = remove_extra_indents(sql2)

    print(f"query {sql1}")
    df,err = do_query(cnx, sql1)
    print(df)

    print("-"*40)
    print(f"insert row: {sql2}")
    err_code = do_sql(cnx, sql2)

    print("-"*40)
    print(f"query {sql1}")
    df,err = do_query(cnx, sql1)
    print(df)
