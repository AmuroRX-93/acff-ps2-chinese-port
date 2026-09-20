#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
iso="$PWD/ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso"
if [ ! -f "$iso" ]; then
  echo '差分包请先运行一键汉化或升级，然后用模拟器打开生成的 ISO。'
  read -r -p '按回车关闭……' _reply
  exit 1
fi
for app in /Applications/ARMSX2.app "$HOME/Applications/ARMSX2.app" /Applications/PCSX2.app "$HOME/Applications/PCSX2.app"; do
  if [ -d "$app" ]; then
    open -a "$app" --args -- "$iso"
    exit $?
  fi
done
echo '没有找到已安装的 ARMSX2 或 PCSX2。请打开自己的 PS2 模拟器并选择包内 ISO。'
open -R "$iso"
read -r -p '按回车关闭……' _reply
