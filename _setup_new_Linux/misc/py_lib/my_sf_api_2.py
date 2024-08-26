#! python3

"""
# module my_sf_api
# to extract data from SF using API
# August 2020
"""

import sys,os, collections, requests, time, pprint
import pandas as pd
import numpy as np

from simple_salesforce import Salesforce
import myutil_dt, myutil

params_prod = {
    "username"      :'__CHANGEME__', 
    "password"      :'__CHANGEME__', 
    "security_token":'__CHANGEME__', 
    "domain"        :'login',
    "version"       :'42.0',
}

params_sand = {
    "username"      :'__CHANGEME__', 
    "password"      :'__CHANGEME__', 
    "security_token":'__CHANGEME__', 
    "domain"        :'test',
    "version"       :'42.0',
}

# --------------------------------------------------------------
# --------------------------------------------------------------
def get_sf(params=None):
    """
    # connects to SF instance
    # returns sf - the connection object
    # needs a params dictionary in the form:
    #    params = {
    #        "username"      : 'user@domain.com',
    #        "password"      : 'somePassword',
    #        "security_token": 'someToken',
    #        "domain"        : "login",  # login for prod, test for sand
    #        "version"       : "42.0", 
    #    }
    """
    login_success = False
    sleep_secs = 10
    N_try_max = 9
    N_try = 0
    # ---------------------------------
    while (login_success == False) and (N_try < N_try_max):
        t1 = time.time()
        my_ts = myutil_dt.now_str()
        N_try += 1
        print("\n--------------------\n")
        print(f"login attempt # {N_try} of {N_try_max} at {my_ts}\n")
        try:
            sf = Salesforce(**params)
            login_success = True
            print(f"Login success on attempt # {N_try}")
        except:
            print(f"FAILED to login attempt # {N_try} of {N_try_max}")
            time.sleep(sleep_secs)

    if not login_success:
        print("FATAL ERROR, failed to login into Salesforce, exiting ...")
        sys.exit(1)
    # ---------------------------------

    return sf

# --------------------------------------------------------------
def row_to_dict(rec,sep):
    """
    # called from conv_res_to_df()
    # receives "rec" - an ordered dict
    #   (may have hierarchical structure)
    # we use BFS (Breadth First Search) with a queue approach
    # to parse the structure, flatten it
    # and return data as a dictionary
    # We concatenate names recursively via "_":
    # Opportunity.Owner.Name => Opportunity_Owner_Name
    """
    SA = set(["attributes"])
    mykeys = list(set(rec.keys()) - SA)
    if not len(mykeys):
        return mydict

    queue  = []
    for kk in mykeys:
        queue.append(("", kk, rec[kk])) # (name, key, val)

    mydict = {}

    while len(queue):
        name, kk, vv = queue.pop(0)
        name = kk if (name == "") else (name + sep + kk)
        if type(vv) != collections.OrderedDict:
            mydict[name] = vv
        else:
            mykeys = list(set(vv.keys()) - SA)
            for kk2 in mykeys:
                queue.append((name, kk2,vv[kk2]))

    return mydict

# --------------------------------------------------------------
def get_columns(rec,sep):
    """
    # accepts one record_installed
    # returns a list of columns in correct order
    """
#    print("-"*40)
#    pprint.pprint(rec)
#    print("-"*40)

    mykeys = list(rec.keys())
    if not len(mykeys):
        return []
    queue  = []
    for ii in range(len(mykeys)):
        kk = mykeys[ii]
        if kk == "attributes":
            continue
        ss = f"{ii:>03d}"   # convert integer into zero-padded string "002"
        queue.append(("", kk, ss, rec[kk])) # (name, key, ii, val)

    mylist = []

    while len(queue):
        name, kk, ss, vv = queue.pop(0)
        name = kk if (name == "") else (name + sep + kk)
        if type(vv) != collections.OrderedDict:
            mylist.append([ss,name])
        else:
            mykeys = list(vv.keys())
            for ii2 in range(len(mykeys)):
                kk2 = mykeys[ii2]
                if kk2 == "attributes":
                    continue
                ss2 = f"{ii2:>03d}"
                queue.append((name, kk2, ss+ss2, vv[kk2]))

    # mylist consists of 2-element lists [ss,name]
    # first elements may have different length
    # (depending on depth in the record)
    # we need to append zeros to make all of them the same length
    max_len = 0
    for ss,name in mylist:
        if len(ss) > max_len:
            max_len = len(ss)
    for ii in range(len(mylist)):
        ss = mylist[ii][0]
        N = max_len - len(ss)
        if N > 0:
            ss += '0'*N
            mylist[ii][0] = ss
    mylist = sorted(mylist)
    mylist = [elem[1] for elem in mylist]

    return mylist

# --------------------------------------------------------------
def combine_two(cols_merged, cols_row, sep):
    """
    # merges two lists of columns, returns one list
    """
    # most commonly the two lists are equal - so just return it unchanged
    if cols_merged == cols_row:
        return cols_merged
    if len(cols_merged) <= 0:
        return cols_row
    elif len(cols_row) <= 0:
        return cols_merged
    # --------------------------------------
    # we are here if the lists are not empty and not equal
    # we actually need to do the merge
    # To do this we will combine columns with the same "top"
    # So we convert list [ 'a', 'b', 'b_zzzz_c']
    # into OrderedDict([  'a':[a],   'b':['b', 'b_zzzz_c'] ])
    # Note that the number of tops should always be the same between two lists.
    # And columns with the same tops should be next to each other in a list.
    # And the order of those tops in each list should be the same.
    #
    # Then we combine the lists by combining the values,
    # remove duplicates and sorting the values, and 
    # finally just append these values together into one list
    # --------------------------------------
    ord_dict = collections.OrderedDict()
    for col in cols_merged + cols_row:
        top = col.split(sep)[0]
        # print(f"top={top}")
        if top not in ord_dict:
            # print(f"creating top={top}, val={[col]}")
            ord_dict[top] = [col]
        else:
            # print(f"adding   top={top}, val={[col]}")
            ord_dict[top] = ord_dict[top] + [col]
    # --------------------------------------
    combined = []
    for kk in ord_dict:
        mylist = sorted(set(ord_dict[kk]))
        combined.extend(mylist)

    return combined

# --------------------------------------------------------------
def combine_cols_from_all_rows(cols_all_rows=None, sep=None):
    """
    # accepts a list of lists of columns for all rows.
    # separator inside hierarchical names is "_::::_"
    # returns one cols_merged by including all names in proper order
    # also includes set cols2delete (the tops of hierarchies)
    """
    cols_merged = []
    cols2delete = set()
    if len(cols_all_rows) <= 0:
        return cols_merged, cols2delete

    cols_merged = cols_all_rows[0]
    for cols_row in cols_all_rows:
        cols_merged = combine_two(cols_merged, cols_row, sep)

    # decide which columns to delete
    # by finding all hierarchical parents 
    for col in cols_merged:
        if sep not in col:
            continue
        parts = col.split(sep) # at least 2 parts
        parts.pop()            # remove last part,
        ss = sep.join(parts)   
        cols2delete.add(ss)    
        
    return cols_merged, list(cols2delete)

# --------------------------------------------------------------
def conv_res_to_df(result=None):
    """
    # accepts result (response) object of running SOQL query
    # returns pandas DataFrame
    """
    mydata = []
    mycols = []
    list_of_dicts = []
    cols_all_rows = []
    sep = "_ZZZZ_"  # separator to join the hierarchical column names
    for rec in result['records']: # rec is OrderedDict
        cols_all_rows.append(get_columns(rec, sep))
        mydict = row_to_dict(rec, sep)
        list_of_dicts.append(mydict)
    cols, cols2delete = combine_cols_from_all_rows(cols_all_rows, sep)     
    df = pd.DataFrame(list_of_dicts, columns=cols)
    # --------------------------
    # delete tops of hierarchies
    if len(cols2delete):
        for col in cols2delete:
            if col in df.columns:
                del df[col]
    # --------------------------
    # change separator in hierarchical names to "_"
    cols = df.columns
    cols_new = []
    for col in cols:
        if sep in col:
            col2 = col.replace(sep,"_")
        else:
            col2 = col
        cols_new.append(col2)
    df.columns = cols_new
    # --------------------------
    N_rows = len(df)
    print(f"Created pandas DataFrame with {N_rows:<,d} rows", )
    return df

# --------------------------------------------------------------
def test_soql(params=None, label=None):
    """
    # runs simple test for a provided Environment
    #   test_sf(params_prod, "PROD")
    #   test_sf(params_sand, "SAND")
    """
    t1 = time.time()
    print(f"\n\nConnecting to {label}")
    sf = get_sf(params=params)
#    soql = "Select Id, firstname, lastname FROM Contact LIMIT 5"

    soql = """
        SELECT 
            Name, 
            StageName,
            Opportunity.owner.name,
            Account.name,
            CreatedDate,
            CloseDate
        FROM
           Opportunity
        WHERE 
           CALENDAR_YEAR(CreatedDate) = 2020
           And
           CloseDate < 2020-12-01
        ORDER BY
            CreatedDate
        LIMIT 5"""

    print(soql)
    result = sf.query_all(soql)
    print("Query finished, received records:", result['totalSize'])
    t2 = time.time()
    print("Query finished: elapsed seconds = %.3f" % (t2-t1))
    df = conv_res_to_df(result)
    print(f"columns = {list(df.columns)}")
    print(df)
    mydate = myutil_dt.now_str_for_log()
    fname = "/tmp/test_my_sf_api_"+mydate+".csv"
    print(f"writing pandas DataFrame to file {fname}")
    df.to_csv(fname, index=False)
    t2 = time.time()
    print("CSV file written: elapsed seconds = %.3f" % (t2-t1))

# --------------------------------------------------------------
if __name__=='__main__':
    test_soql(params_prod, "PROD")
#    test_soql(params_sand, "SAND")
    print("\n\nDONE")
