@echo off
title Pokemon Champions Match Tracker
cd /d "%~dp0"

echo ====================================================
echo Starting Pokemon Champions Matchup Tracker...
echo Opening Dashboard at: http://localhost:5050
echo ====================================================

start http://localhost:5050
python server.py
pause
