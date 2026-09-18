#!/bin/bash
cd "$(dirname "$0")" || exit 1
PY=""
for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
  if "$candidate" -c 'import sys;sys.exit(sys.version_info < (3,10))' >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done
if [ -z "$PY" ]; then
  echo '需要 Python 3.10 或以上。请从 https://www.python.org/downloads/ 安装后重新打开。'
else
  "$PY" installer/patcher.py "$@"
fi
read -r -p '按回车关闭。' _reply
