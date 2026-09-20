@echo off
chcp 65001 >nul
cd /d "%~dp0"
:menu
cls
echo ACFF - PSP 汉化资源移植至 PS2 - v0.12.14
echo.
if exist "游戏\ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso" (
 echo 1  开始游戏（直接按回车）
 echo 2  安装到你的游戏目录
) else (
 echo 1  一键汉化 / 升级旧版（直接按回车）
)
echo 3  校验镜像
echo 4  查看详细说明
echo 0  退出
set "choice=1"
set /p "choice=请选择："
if "%choice%"=="0" exit /b
if "%choice%"=="4" (
 start "" notepad.exe "说明\使用说明.md"
 goto menu
)
set "action="
if "%choice%"=="1" (
 if exist "游戏\ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso" (set "action=start") else (set "action=patch")
)
if "%choice%"=="2" set "action=install"
if "%choice%"=="3" set "action=verify"
if not defined action goto menu
where py >nul 2>nul
if not errorlevel 1 (
 py -3 工具\installer\manage.py %action%
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo 请安装 Python 3.10+，并勾选 Add Python to PATH：https://www.python.org/downloads/
 ) else (
  python 工具\installer\manage.py %action%
 )
)
pause
goto menu
