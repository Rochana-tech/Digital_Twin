@echo off
set ROOT=%~dp0
start "Digital Twin Backend" cmd /k "cd /d %ROOT%backend && py -m pip install -r requirements.txt && py integration_server.py --demo"
start "Digital Twin Dashboard" cmd /k "cd /d %ROOT% && npm install && npm run dev"
