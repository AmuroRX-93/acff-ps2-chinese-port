# ACFF v0.13.0 影片升级

仅适用于 v0.12.14 汉化 ISO。请从本仓库 v0.13.0-movies-beta Release 下载升级 ZIP；这里是安装器源码，不含差分载荷或完整游戏。

Python 3.8+，标准库：

```sh
python3 movie_upgrade.py "v0.12.14.iso" "v0.13.0.iso"
python3 test_movie_upgrade.py
```

运行升级需要将 Release 包内 movie_patch.zip 放在安装器同目录。硬编码核对输入与输出 SHA-256；原镜像保留，独立临时文件验证后提交，不覆盖已有输出。测试使用临时小样覆盖失败分支；完整 ISO 重建报告随 Release 提供。

47 段候选已通过离线技术校验，实际游戏验证范围和保留内容详见 RELEASE_NOTES.md / validation.json。
