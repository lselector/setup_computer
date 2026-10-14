@echo off
rem ghopen - open current repo/branch/folder on GitHub in browser.
rem If not inside a git repo with an origin, open user's GitHub page.
setlocal

set "repo="
for /f "delims=" %%i in ('git remote get-url origin 2^>nul') do set "repo=%%i"
if not defined repo (
    start "" "https://github.com/lselector"
    exit /b 0
)
set "repo=%repo:git@github.com:=%"
set "repo=%repo:https://github.com/=%"
if /i "%repo:~-4%"==".git" set "repo=%repo:~0,-4%"

for /f "delims=" %%i in ('git branch --show-current') do set "branch=%%i"
set "relpath="
for /f "delims=" %%i in ('git rev-parse --show-prefix') do set "relpath=%%i"
if defined relpath if "%relpath:~-1%"=="/" set "relpath=%relpath:~0,-1%"

start "" "https://github.com/%repo%/tree/%branch%/%relpath%"
endlocal
