@echo off
echo Starting GNN-MIP Facility Siting Simulation...
python "%~dp0simulate_siting.py"
echo.
echo Simulation completed. Press any key to exit.
pause > nul
