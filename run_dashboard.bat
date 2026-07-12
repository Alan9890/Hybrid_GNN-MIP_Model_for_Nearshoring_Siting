@echo off
title GNN-MIP Siting Dashboard Dev Server
echo =======================================================================
echo          GNN-MIP INDUSTRIAL SITING INTERACTIVE DASHBOARD
echo =======================================================================
echo.
echo Starting local Python HTTP server on port 8000...
start /b python -m http.server 8000
echo.
echo Opening dashboard in your default browser...
start http://localhost:8000/index.html
echo.
echo -----------------------------------------------------------------------
echo Server is running. Press any key to stop the server and exit.
echo -----------------------------------------------------------------------
pause > nul
echo.
echo Stopping Python server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr 8000') do taskkill /f /pid %%a > nul 2>&1
echo Done.
