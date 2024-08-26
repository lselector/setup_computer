#! /bin/bash

# ------------------------------------
# set_links_py_lib.bash
# ------------------------------------
# this script should run like this:
#     cd $HOME/docs/py_ib
#     bash set_links_py_lib.bash
# ------------------------------------

myfiles="ipython_debug.py
         mybag.py
         mylog.py
         myutil.py
         myutil_dt.py
         myutil_msdw.py
         myutil_mysql.py
         myutil_postgresql.py
         util_jupyter.py
         util_models.py
         util_states.py"

for f in $myfiles
do
    echo "processing $f"
    if [ -f "$f" ]; then
        echo "    removing $f"
        rm -rf $f
    fi

    echo "    linking $f"
    ln -s $HOME/Documents/GitHub/setup_computer/py_lib/$f  $f

done
