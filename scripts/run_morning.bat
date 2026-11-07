@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\activate.bat" (
  echo Missing .venv. Follow docs/START_HERE.md first.
  exit /b 1
)
call ".venv\Scripts\activate.bat"
if not exist "logs" mkdir "logs"
echo [%date% %time%] Starting THE DAWG AGENT >> "logs\morning.log"
dawg run >> "logs\morning.log" 2>&1
