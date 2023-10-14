
"""
# function clean_state(ss) accepts a string, returns clean abbreviation or "_"
"""

import os
import sys
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

# --------------------------------------------------------------
def remove_vowels_and_dups(ss):
    """
    # remove vowels and repeated characters from string
    """
    mylist = []
    mychar = ""
    for ch in ss:
        ch_low = ch.lower()
        if ch_low in 'aeiou':
            continue
        if ch_low == mychar:
            continue
        mychar = ch_low
        mylist.append(ch)

    return "".join(mylist)


# --------------------------------------------------------------
state_abbrev_set = set(
    ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
     'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
     'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
     'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW',
     'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VI',
     'VA', 'WA', 'WV', 'WI', 'WY']
)


# --------------------------------------------------------------
state_to_abbrev_dict = {
    'ALABAMA': 'AL',
    'ALASKA': 'AK',
    'ARIZONA': 'AZ',
    'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA',
    'COLORADO': 'CO',
    'CONNECTICUT': 'CT',
    'DELAWARE': 'DE',
    'DISTRICT OF COLUMBIA': 'DC',
    'FLORIDA': 'FL',
    'GEORGIA': 'GA',
    'HAWAII': 'HI',
    'IDAHO': 'ID',
    'ILLINOIS': 'IL',
    'INDIANA': 'IN',
    'IOWA': 'IA',
    'KANSAS': 'KS',
    'KENTUCKY': 'KY',
    'LOUISIANA': 'LA',
    'MAINE': 'ME',
    'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA',
    'MICHIGAN': 'MI',
    'MINNESOTA': 'MN',
    'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO',
    'MONTANA': 'MT',
    'NEBRASKA': 'NE',
    'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH',
    'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM',
    'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC',
    'NORTH DAKOTA': 'ND',
    'NORTHERN MARIANA ISLANDS':'MP',
    'OHIO': 'OH',
    'OKLAHOMA': 'OK',
    'OREGON': 'OR',
    'PALAU': 'PW',
    'PENNSYLVANIA': 'PA',
    'PUERTO RICO': 'PR',
    'RHODE ISLAND': 'RI',
    'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD',
    'TENNESSEE': 'TN',
    'TEXAS': 'TX',
    'UTAH': 'UT',
    'VERMONT': 'VT',
    'VIRGIN ISLANDS': 'VI',
    'VIRGINIA': 'VA',
    'WASHINGTON': 'WA',
    'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI',
    'WYOMING': 'WY',
}

# --------------------------------------------------------------
# below dictionary is created by removing vowels 
# and duplicate characters from full names

state_no_vowel_dict = {
    'LBM': 'AL',
    'LSK': 'AK',
    'RZN': 'AZ',
    'RKNS': 'AR',
    'CLFRN': 'CA',
    'CLRD': 'CO',
    'CNCTCT': 'CT',
    'DLWR': 'DE',
    'DSTRCT F CLMB': 'DC',
    'FLRD': 'FL',
    'GRG': 'GA',
    'HW': 'HI',
    'DH': 'ID',
    'LNS': 'IL',
    'NDN': 'IN',
    'W': 'IA',
    'KNS': 'KS',
    'KNTCKY': 'KY',
    'LSN': 'LA',
    'MN': 'ME',
    'MRYLND': 'MD',
    'MSCHSTS': 'MA',
    'MCHGN': 'MI',
    'MNST': 'MN',
    'MSP': 'MS',
    'MSR': 'MO',
    'MNTN': 'MT',
    'NBRSK': 'NE',
    'NVD': 'NV',
    'NW HMPSHR': 'NH',
    'NW JRSY': 'NJ',
    'NW MXC': 'NM',
    'NW YRK': 'NY',
    'NRTH CRLN': 'NC',
    'NRTH DKT': 'ND',
    'NRTHRN MRN SLNDS': 'MP',
    'H': 'OH',
    'KLHM': 'OK',
    'RGN': 'OR',
    'PL': 'PW',
    'PNSYLVN': 'PA',
    'PRT RC': 'PR',
    'RHD SLND': 'RI',
    'STH CRLN': 'SC',
    'STH DKT': 'SD',
    'TNS': 'TN',
    'TXS': 'TX',
    'TH': 'UT',
    'VRMNT': 'VT',
    'VRGN SLNDS': 'VI',
    'VRGN': 'VA',
    'WSHNGTN': 'WA',
    'WST VRGN': 'WV',
    'WSCNSN': 'WI',
    'WYMNG': 'WY'
}

# --------------------------------------------------------------
def clean_state(ss):
    """
    # receives a string containing US State, which can be misspelled.
    # tries to convert it into 2-char abbreviation
    # returns this abbreviation - or "_" if couldn't do it.
    """
    ss = str(ss).strip().upper()
    if ss in state_abbrev_set:
        return ss
    elif ss in state_to_abbrev_dict:
        return state_to_abbrev_dict[ss]
    # ----------------------------------
    # try to match with removed vowels and duplicates
    ss = remove_vowels_and_dups(ss)
    if ss in state_no_vowel_dict:
        return state_no_vowel_dict[ss]
    else:
        return "_"

# --------------------------------------------------------------
# --------------------------------------------------------------
