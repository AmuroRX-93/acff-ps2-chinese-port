#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo '需要 Python 3.10 或以上：https://www.python.org/downloads/'
  read -r -p '按回车退出……' _reply
  exit 1
fi
python3 installer/manage.py verify "$@"
_status=$?
read -r -p '按回车关闭……' _reply
exit "$_status"
