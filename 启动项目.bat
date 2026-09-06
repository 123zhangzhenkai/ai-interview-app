@echo off
chcp 65001
cd /d "%~dp0"
start "Redis" cmd /k "cd /d C:\Users\张\Desktop\Redis && redis-server.exe redis.windows.conf"
start "后端" cmd /k "cd backend && uvicorn app.main:app --reload"
start "前端" cmd /k "cd web && python -m http.server 5173"
timeout /t 4
start http://127.0.0.1:5173
exit