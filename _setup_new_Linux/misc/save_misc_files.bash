#! /bin/bash

# -----------------------------------------------
# save_misc_files.bash
#
# save misc dot and config files into  directory /data/code/misc/SAVED/
#
# rsync -avzh src dst/
#
# -a - archive mode; equals -rlptgoD
#      -r - recursive
#      -l - user
#      -p - partial progress ?
#      -t - modification times
#      - - group
#      - - owner
#      -D - devices
# -v - verbose
# -z - compress
# -h - human readable
#
# -c = --checksum - copy only if different (ignores timestamp)
# -----------------------------------------------
set -x #echo on
echo "------------------------------------------"
echo "Starting: " $(date)
export HOME=/home/azureuser
export dst=/data/code/misc/SAVED

crontab -l > /tmp/crontab.txt
rsync -c    /tmp/crontab.txt           $dst/crontab.txt

cat ~/.bash_history > /tmp/bash_history.txt
rsync -c  /tmp/bash_history.txt        $dst/bash_history.txt

pip freeze >$dst/py_pip_freeze.txt 2>&1
conda list >$dst/py_conda_list.txt 2>&1

rsync -avzh $HOME/.vimrc               $dst/_vimrc.txt
rsync -avzh $HOME/.bashrc              $dst/_bashrc.txt
rsync -avzh $HOME/.bash_aliases        $dst/_bash_aliases.txt
rsync -avzh $HOME/.bash_profile        $dst/_bash_profile.txt
rsync -avzh $HOME/.bashrc_crontab      $dst/_bashrc_crontab.txt
rsync -avzh $HOME/.git-completion.bash $dst/_git-completion.bash
rsync -avzh $HOME/.gitconfig           $dst/_gitconfig.txt
rsync -avzh $HOME/.gitexcludes         $dst/_gitexcludes.txt
rsync -avzh $HOME/.inputrc             $dst/_inputrc.txt
rsync -avzh $HOME/.mygit               $dst/_mygit.txt
rsync -avzh $HOME/.myvv                $dst/_myvv.txt
rsync -avzh $HOME/.profile             $dst/_profile.txt
rsync -avzh /etc/fstab                 $dst/etc_fstab.txt
rsync -avzh /etc/nginx                 $dst/
echo "Finished: " $(date)

