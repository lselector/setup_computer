"""
# module my_sf_api
# to extract data from Salesforce using API
"""

import sys,os
import pandas as pd
import numpy as np

from simple_salesforce import Salesforce
import requests, time
import myutil_dt

params_prod = {
    "grant_type"    : "password",
    "client_id"     : "...",                 # Consumer Key
    "client_secret" : "...",                 # Consumer Secret
    "username"      : "myuser@mydomain.com", # The email you use to login
    "password"      : "mypassword"           # Concat your password and your security token
}

params_sand = {
    "grant_type"    : "password",
    "client_id"     : "...",                 # Consumer Key
    "client_secret" : "...",                 # Consumer Secret
    "username"      : "myuser@mydomain.com", # The email you use to login
    "password"      : "mypassword"           # Concat your password and your security token
}

url_prod = "https://login.salesforce.com/services/oauth2/token"
url_sand = "https://test.salesforce.com/services/oauth2/token"

# --------------------------------------------------------------
def get_sf(myurl=None, params=None):
    """
    # connects to Salesforce instance
    # returns sf - the connection object
    """
    r = requests.post(myurl, params=params)
    access_token = r.json().get("access_token")
    instance_url = r.json().get("instance_url")
    print("Access Token:", access_token)
    print("Instance URL", instance_url)

    sf = Salesforce(instance_url = instance_url, session_id = access_token)

    return sf

# --------------------------------------------------------------
def conv_res_to_df(result=None):
    """ convert extracted data to Pandas DataFrame """
    mydata = []
    mycols = []
    first_pass = True
    for rec in result['records']:
        myrow = []
        for field in rec:
            if field == "attributes":
                continue
            if first_pass:
                mycols += [field]
            myrow += [rec[field]]
        first_pass = False
        #print(myrow)
        mydata += [myrow]
    df = pd.DataFrame(mydata, columns = mycols)
    print("Created pandas dataframe with length ",len(df))
    return df

# --------------------------------------------------------------
if __name__=='__main__':
    t1 = time.time()
    sf = get_sf(myurl=url_sand, params=params_sand)
    soql = "Select Id FROM SomeObject LIMIT 5"
    result = sf.query_all(soql)
    print("Query finished, received records:", result['totalSize'])
    t2 = time.time()
    print("Query finished: elapsed seconds = %.3f" % (t2-t1))
    df = conv_res_to_df(result)

    mydate = myutil_dt.now_str_for_log()
    fname = "test_sand_SomeObject_"+mydate+".csv"
    print("writing to file",fname)
    df.to_csv(fname, index=False)
    t2 = time.time()
    print("CSV file written: elapsed seconds = %.3f" % (t2-t1))

