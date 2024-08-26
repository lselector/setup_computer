#! /bin/bash

# ------------------------------------
# set_links_bin.bash
# ------------------------------------
# this script should run like this:
#     cd $HOME/docs/py_ib
#     bash set_links_bin.bash
# ------------------------------------

if [ -f "gistall" ]; then
    echo "    removing gistall"
    rm -rf gistall
fi

ln -s gistall.py gistall
