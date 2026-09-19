@echo off
cd /d "%~dp0"
title Industrial AI - All Layers
where py >nul 2>nul
if %errorlevel%==0 (
  py run_all.py
) else (
  python run_all.py
)
pause
