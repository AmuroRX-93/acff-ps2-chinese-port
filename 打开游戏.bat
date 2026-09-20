@echo off
chcp 65001 >nul
setlocal
set "game=%~dp0ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso"
if not exist "%game%" (
  echo 差分包请先运行一键汉化或升级，再用模拟器打开生成的 ISO。
  pause
  exit /b 1
)
echo 请拖入你已安装的 PCSX2 的 exe 文件，按回车：
set /p "emulator="
set "emulator=%emulator:"=%"
if not exist "%emulator%" (
  echo 找不到该模拟器。请直接从模拟器打开包内 ISO。
  pause
  exit /b 1
)
start "" "%emulator%" -- "%game%"
