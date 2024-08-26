"""
# ipython_debug.py
# utility module to provide function "debug_here()"
# to be used for debugging under ipython.
# 
# import like this
#
# import ipython_debug
# tested for python 3.7
"""

import os, sys
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
import IPython

# --------------------------------------------------------------
def run_from_ipython():
    """
    # boolean test if we are running from ipython
    """
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

# --------------------------------------------------------------
def sys_exit_1():
    """
    # this function is called instead of Tracer
    # when running script without iPython
    """
    print("debug_here() only works in iPython. Exiting...")
    sys.exit(1)

# --------------------------------------------------------------
# The code below is executed when importing this module
# It adds function debug_here() to enter iPython debugger
# When running without iPython, it will do sys.exit(1) instead.
# --------------------------------------------------------------
if run_from_ipython():
    # import Tracer class
    from IPython.core.debugger import Pdb
    # get yourself a tracer
    pdb = Pdb()
    debug_here = pdb.set_trace
else:
    debug_here = sys_exit_1


# DeprecationWarning: `Tracer` is deprecated since version 5.1, 
#     directly use `IPython.core.debugger.Pdb.set_trace()`