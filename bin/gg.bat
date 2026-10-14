@echo off
rem gg - runs short sequence to submit and push an update

git add .
git commit -m "update"
git push
call "%~dp0gist.bat"
