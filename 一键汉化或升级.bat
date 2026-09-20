@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 installer\manage.py patch %*
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo 请安装 Python 3.10 或以上：https://www.python.org/downloads/
  ) else (
    python installer\manage.py patch %*
  )
)
pause
