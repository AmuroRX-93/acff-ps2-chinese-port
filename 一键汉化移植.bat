@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 -c "import sys;sys.exit(sys.version_info < (3,10))" >nul 2>&1
if not errorlevel 1 (
  py -3 installer\patcher.py %*
) else (
  python -c "import sys;sys.exit(sys.version_info < (3,10))" >nul 2>&1
  if not errorlevel 1 (
    python installer\patcher.py %*
  ) else (
    echo 需要 Python 3.10 或以上，请从 https://www.python.org/downloads/ 安装。
  )
)
pause
