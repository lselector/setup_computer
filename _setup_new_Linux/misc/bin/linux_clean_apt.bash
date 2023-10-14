#! /bin/bash

# ---------------------------------------------
# maintenance script
# run it after system upgrades (after reboots)
# to keep system libraries clean
# by Lev Selector
# January 5, 2022
# ---------------------------------------------

myskip () { echo -e "\n"; }

echo -e "\nSTARTING\n"

sudo apt-get --yes update
myskip
sudo apt-get --yes upgrade
myskip
sudo apt-get --yes autoremove --purge
myskip
sudo apt-get --yes autoclean
myskip
sudo journalctl --vacuum-time=10d

echo -e "\nALL DONE\n"

