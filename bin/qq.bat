@echo off
rem qq - simply runs gist command
echo ------------------------------------- files which diff from remote repo
git fetch
git diff --name-only
echo ------------------------------------- files changed locally
git status .
echo -------------------------------------
