@echo off
rem Refresh all data from this laptop, then push it to GitHub.
rem (CBSL blocks GitHub's cloud computers, so this laptop does the CBSL part.)

cd /d "C:\Users\amaya\Downloads\modelx-invest\modelx-invest\ModelX"
set LOG=refresh_log.txt
set PY=..\.venv\Scripts\python.exe

echo ===== %date% %time% ===== >> %LOG%

rem 1. get whatever the GitHub robot has already saved
git pull --rebase --autostash >> %LOG% 2>&1
if errorlevel 1 goto fail

rem 2. run the whole pipeline
"%PY%" src\data\run_pipeline.py >> %LOG% 2>&1
if errorlevel 1 goto fail

rem 3. save any new data and send it to GitHub
git add data >> %LOG% 2>&1
git diff --cached --quiet
if errorlevel 1 git commit -m "data: local refresh %date%" >> %LOG% 2>&1
git push >> %LOG% 2>&1
if errorlevel 1 goto fail

echo DONE OK >> %LOG%
exit /b 0

:fail
echo FAILED - see lines above >> %LOG%
exit /b 1
