
"""
# utility functions to work with PostgreSQL 
# On RHEL Linux:
#   yum install postgresql-server
#   postgresql-setup initdb
#   systemctl enable postgresql.service
#   systemctl start postgresql.service
#
# for restart: sudo service postgresql restart
# ps auxww: /usr/bin/postgres -D /var/lib/pgsql/data -p 5432
#
# switch to postgres unix user:
#     sudo su - postgres
#
# edit file pg_hba at the bottom - change host connections to password mode
#    
#    vi /var/lib/pgsql/data/pg_hba.conf
#    
#    # TYPE  DATABASE        USER            ADDRESS                 METHOD
#    local   all             all                                     ident
#    host    all             all             127.0.0.1/32            password
#    host    all             all             ::1/128                 password
#    
#    # start psql client
#    psql
#      create database amz;
#      create user lev01 with superuser createdb createrole login replication password 'something';
#      \du       -- to show users
#      \c amz
#      create table tab1 (col1 int);
#      \d
#      \d tab1
#      \q
#    
#    # now try to connect to the database using regular connect command:
#    #   psql -U lev01 -h localhost -d amz
# --------------------------------------------------------------
# On Ubuntu - google instructions, for example:
#   https://phoenixnap.com/kb/how-to-install-postgresql-on-ubuntu

# Add PostgreSQL Repository
#      sudo apt-get install wget ca-certificates
#      wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
#      sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ 'lsb_release -cs'-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
#    
#      sudo apt-get update
#      sudo apt-get install postgresql postgresql-contrib
#
# switch to postgres user
#      sudo su - postgres
#  start psql client
#      psql
# --------------------------------------------------------------
# On MacOS - download dmg file from here:
#   https://www.postgresql.org/download/macosx/
#
# Actually easier way is to install Postgress.app from here:
#   https://postgresapp.com/downloads.html
# Start the Postgress.app and play with it as described in this short video
#    -  https://www.youtube.com/watch?v=WcCjNGb8g0o
# Note - you can switch from default terminal to iTerm in preferences.
# Note - the app starts the server - and sets it to start on login.
#
# Then run "ps auxww | grep -i postgres" to find location of "bin server,
# and add it to your $PATH (in .bashrc ?) like that:
#    PATH=$PATH:/Applications/Postgres.app/Contents/Versions/13/bin
#
# and now in terminal you can type "psql" - it opens the db prompt.
#
# --------------------------------------------------------------
# To work with python:
#     pip install psycopg2
#
"""

# this small python test should work if you use Postgress.app:

import os, sys
import numpy as np
import pandas as pd
import psycopg2

print("connecting")
conn = psycopg2.connect(database='testdb', host='localhost', user='postgres', password='')

print("creating cursor")
cur = conn.cursor()

print("drop table test1")
cur.execute("DROP TABLE IF EXISTS test1")
print("create table test1")
cur.execute("""CREATE TABLE test1 (
        id          serial PRIMARY KEY,
        col1        varchar(2056),
        col2        varchar(128)
    );""")
conn.commit()

print("insert into test1")
cur.execute("INSERT INTO test1 (col1, col2) VALUES (%s, %s) RETURNING id", ('mama1','papa1'))
print("insert into test1")
cur.execute("INSERT INTO test1 (col1, col2) VALUES (%s, %s) RETURNING id", ('mama2','papa2'))
conn.commit()

print("fetch primary key")
myid = cur.fetchone()[0]
print(myid)

print("select everything from table")
cur.execute("""SELECT * from test1""")
rows = cur.fetchall()  # list of tuples
colnames = [desc[0] for desc in cur.description]
conn.commit()

print("printing rows as list of tuples")
print(rows)
print("printing rows as pandas DataFrame")
df = pd.DataFrame(rows, columns=colnames)
print(df)
print("done")

"""
# Here is how to save query result into Pandas DataFrameL
#    df = pd.read_sql_query(sql, dbConnection)
#    df = ps.read_sql("select * from \"StudentScores\"", dbConnection)
# or    
#    tupples = cursor.fetchall()
#    df = pd.DataFrame(tupples, columns=colnames)

# https://towardsdatascience.com/python-and-postgresql-how-to-access-a-postgresql-database-like-a-data-scientist-b5a9c5a0ea43
# https://naysan.ca/2020/05/31/postgresql-to-pandas/
# https://pythontic.com/pandas/serialization/postgresql
# https://medium.com/analytics-vidhya/part-3-5-pandas-dataframe-to-postgresql-using-python-d3bc41fcf39
https://stackoverflow.com/questions/10252247/how-do-i-get-a-list-of-column-names-from-a-psycopg2-cursor
"""
