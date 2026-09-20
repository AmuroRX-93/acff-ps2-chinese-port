# ACFF — PSP 汉化资源移植至 PS2 v0.12.14

**这是既有 PSP 民间汉化资源的 PS2 移植版，公开测试、无偿分享。**
原 PSP 汉化：becky（翻译）、ben（文本导出）、WEFGOD（字库与导入）等；PS2 移植发布：AmuroRX-93（Bilibili：Scorchfrost）。完整致谢与原始发布地址见 `docs/CREDITS.md`。

## 整合包：解压即可打开游戏

完整解压 ZIP。包内 `ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso` 已包含本次全部游戏修改，无需再打补丁。

- Mac：双击 `打开游戏.command`，自动寻找已安装的 ARMSX2 或 PCSX2；也可将镜像拖入模拟器。
- Windows：双击 `打开游戏.bat`，首次按提示拖入自己的 PCSX2 可执行文件；也可直接在模拟器中打开镜像。
- `校验镜像`：检查完整镜像是否与发布版本一致。
- `安装到游戏目录`：将本版镜像复制到你选定的游戏目录，自动校验。已有文件不覆盖，不修改存档或模拟器配置。

模拟器与 BIOS 沿用自己的安装，不捆绑私人配置、记忆卡或即时存档。Mac 打开游戏不要求 Python；安装、升级、校验工具需要 Python 3.10+（仅标准库）。Windows 如果尚未安装 Python，可从 https://www.python.org/downloads/ 安装，并勾选 Add Python to PATH。

## 已经使用 v0.12.6／旧整合包

最省下载量：到 Release 下载 `ACFF_PS2_Port_v0.12.6_to_v0.12.14_Update.zip`，完整解压，运行 `一键汉化或升级`，选择以下任意一个：

1. 上一发布版补丁生成的 v0.12.6 ISO。
2. 旧整合包解压后的 v0.12.6 ISO。
3. 尚未解压的旧镜像整合 ZIP（其中只能有一个 ISO）。

工具按镜像哈希识别版本，文件名可改；不需要重新下载原版或旧版补丁。新 ISO 默认生成在输入文件旁边。需要额外约 3.6 GB 空间，旧文件保持不变。

如果已经下载本次新整合包，直接用包内新镜像即可；需要放回原游戏目录时运行 `安装到游戏目录`，然后在模拟器里选中新版镜像或重新扫描目录。

## 只有原版 ISO

下载 `ACFF_PS2_Port_v0.12.14_Full_Patch.zip`，完整解压，运行 `一键汉化或升级`，选择 PS2 日版 SLPS-25461 原版 ISO。
支持原版大小 3,470,426,112 字节，SHA-256：
`e94c881b242e8614939f39de40e4e0dbd416b3e88c78345dd345a294554d15a9`。

## 存档与切换版本

先在旧游戏里保存并退出。用新 ISO **冷启动**，从游戏内读取原来的记忆卡存档；不要加载旧版即时存档，因为它会带回旧程序和字库。无需重开档，也不要用其他人的记忆卡覆盖自己的。

## 命令行

在完整解压的包目录中运行（Windows 可将 `python3` 换成 `py -3`）：

```sh
# 校验当前整合镜像
python3 installer/manage.py verify
# 安装到已有游戏目录，不覆盖旧镜像
python3 installer/manage.py install "/你的游戏目录"
# 差分包：从原版或 v0.12.6 ISO 生成新版
python3 installer/manage.py patch "/路径/旧版.iso"
# 升级包：直接读取旧整合 ZIP，并指定输出
python3 installer/manage.py patch "/路径/旧整合包.zip" --output "/目标目录/ACFF_v0.12.14.iso"
# 校验其他位置的新镜像
python3 installer/manage.py verify "/路径/ACFF_v0.12.14.iso"
```

Mac 启动命令：
```sh
open -a ARMSX2 --args -- "ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso"
# 或 PCSX2：
open -a PCSX2 --args -- "ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso"
```

如果 Mac 的 .command 没有执行权限，可在终端运行 `bash "打开游戏.command"`；其余入口同理。校验基准见 `RELEASE.json`，包内文件清单见 `SHA256SUMS.txt`。

项目与反馈：https://github.com/AmuroRX-93/acff-ps2-chinese-port
下载：https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/tag/v0.12.14-port-beta
更新范围见 `docs/更新内容.md`。
