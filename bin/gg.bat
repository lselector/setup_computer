@echo off
rem gg - runs short sequence to submit and push an update
rem usage: gg [commit message]   (default message: "update")
setlocal

set "msg=%*"
if not defined msg set "msg=update"
set "msg=%msg:"=%"

git add .
git commit -m "%msg%"
git push
call "%~dp0gist.bat"
endlocal
