#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
iso="$PWD/游戏/ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso"
while true; do
  clear
  echo 'ACFF · PSP 汉化资源移植至 PS2 · v0.12.14'
  echo
  if [ -f "$iso" ]; then
    echo '1  开始游戏（直接按回车）'
    echo '2  安装到你的游戏目录'
  else
    echo '1  一键汉化 / 升级旧版（直接按回车）'
  fi
  echo '3  校验镜像'
  echo '4  查看详细说明'
  echo '0  退出'
  read -r -p '请选择：' choice
  choice=${choice:-1}
  case "$choice" in
    0) exit 0 ;;
    4) open '说明/使用说明.md'; continue ;;
    1)
      if [ -f "$iso" ]; then
        for app in /Applications/ARMSX2.app "$HOME/Applications/ARMSX2.app" /Applications/PCSX2.app "$HOME/Applications/PCSX2.app"; do
          if [ -d "$app" ]; then open -a "$app" --args -- "$iso"; exit $?; fi
        done
        echo '没有找到 ARMSX2 / PCSX2，请在自己的模拟器中打开“游戏”文件夹里的 ISO。'
        open -R "$iso"
        read -r -p '按回车返回……' reply
        continue
      fi
      action=patch ;;
    2) action=install ;;
    3) action=verify ;;
    *) continue ;;
  esac
  if command -v python3 >/dev/null 2>&1; then
    python3 工具/installer/manage.py "$action"
  else
    echo '此功能需要 Python 3.10+：https://www.python.org/downloads/'
  fi
  read -r -p '按回车返回……' reply
done
