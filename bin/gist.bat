@echo off
rem gist - git status - a command to check
rem if anything should be updated from server or committed

echo ------------------------------------- files which diff from remote repo
git fetch
git diff --name-only
echo ------------------------------------- files changed locally
git status .
echo -------------------------------------
