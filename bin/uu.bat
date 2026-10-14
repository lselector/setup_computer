@echo off
rem uu - pull pages while retaining local changes

git stash clear
git stash
git pull
git stash apply
