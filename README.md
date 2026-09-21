# ACFF：PSP 汉化资源移植至 PS2

**这是既有 PSP 民间汉化资源的 PS2 日版移植版，公开测试、无偿分享。**

原 PSP 汉化：**becky（翻译）、ben（文本导出）、WEFGOD（字库与导入）**等。PS2 移植发布：**AmuroRX-93**（Bilibili：Scorchfrost）。完整名单和原始发布位置见[原汉化致谢](docs/CREDITS.md)。PS2 资源适配、补译、代码与排错使用 AI 辅助。

## 基础汉化 + 影片汉化：统一下载入口

**想玩带中文影片的版本，从这里下载即可。两阶段安装，最终得到 v0.13.0 影片汉化测试版。**

| 你现在有的版本 | 第一步：基础汉化至 v0.12.14 | 第二步：影片升级至 v0.13.0 |
|---|---|---|
| PS2 日版 SLPS-25461 原版 ISO | [① 下载基础汉化补丁（554 MB）](https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/download/v0.12.14-port-beta/ACFF_v0.12.14_Full_Patch.zip) | [② 下载影片升级补丁（1.92 GB）](https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/download/v0.13.0-movies-beta/ACFF_v0.13.0_Movies_Update_from_v0.12.14.zip) |
| v0.12.6 汉化 ISO／对应旧整合 ZIP | [① 下载旧版升级补丁（2.2 MB）](https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/download/v0.12.14-port-beta/ACFF_v0.12.14_Update_from_v0.12.6.zip) | [② 下载影片升级补丁（1.92 GB）](https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/download/v0.13.0-movies-beta/ACFF_v0.13.0_Movies_Update_from_v0.12.14.zip) |
| 已有 v0.12.14 汉化 ISO | 无需下载第一步 | [直接下载影片升级补丁（1.92 GB）](https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/download/v0.13.0-movies-beta/ACFF_v0.13.0_Movies_Update_from_v0.12.14.zip) |

### 安装顺序

1. 原版／v0.12.6 用户先下载自己这一行的 **① 和 ②**；已有 v0.12.14 的用户只下载 **②**。这是统一下载入口，不是重复包含两份补丁的新大包，总下载量不会因此缩小。
2. 将所需 ZIP **分别完整解压到不同文件夹**。两阶段一起使用时安装 Python **3.10 或以上**，无需额外 Python 模块。
3. 先运行 **①** 内的 `开始使用.command`（Mac）或 `开始使用.bat`（Windows），选择原版 ISO／对应旧版文件，等它生成并校验 **v0.12.14 ISO**。
4. 再运行 **②** 内的 `Mac_开始升级.command` 或 `Windows_开始升级.bat`，选择上一步生成的 **v0.12.14 ISO**。已有该版本的用户从这一步开始。**影片补丁不能直接套在原版、v0.12.6 或旧整合 ZIP 上。**
5. 完成后用 **v0.13.0 新 ISO 冷启动**，在游戏内读取原记忆卡存档；不要加载升级前的模拟器即时存档。工具保留旧 ISO，每一步都会另生成约 3.47 GB 的新镜像，请为两个阶段分别留出输出空间。

只要把[这个页面](https://github.com/AmuroRX-93/acff-ps2-chinese-port/releases/tag/v0.13.0-movies-beta)分享给朋友，就能找到基础汉化与影片升级。上表链接直接下载对应 Release 附件；不要用 `Code → Download ZIP` 代替补丁。

---

### 基础包说明

GitHub Release 附件包含差分、安装工具和说明，不包含完整游戏 ISO。旧整合 ZIP 可作为 v0.12.14 旧版升级工具的输入；影片升级工具则只接受已经生成的 v0.12.14 ISO。工具不覆盖旧镜像，不修改模拟器配置或记忆卡。

## v0.12.14 基础汉化累计内容

- 移植 PSP 对应的菜单、帮助、对话、提示与公共 AI 调校译文，并适配字符编码和字库。
- 补充 PS2 新闻、队伍介绍、公告、战斗解说、战斗分析、部分图片文字与赛事介绍片中文字幕。
- 修复 AC 测试字库加载的内存压力；保留 5480 个字码及字距，合并重复字形，字库从 14 页降至 11 页，取整后分配量再减小 384 KiB。
- 重建 139 个界面中的 508 条按键说明；补齐纪录详情、装备转移及其他确认提示。
- 统一中文字体为思源黑体，调整左右手、冲刺／跳跃、杜比选项与结算标题。
- 参照 PSP 与确认表统一公司、队伍译名，包括幻影、屋脊、如月、幻影工坊、屋脊工业和屋脊新挑战。

原 PSP 汉化与本次新增范围见致谢与更新记录。本次未新增 PSP 国际版的联赛手动操作玩法。

两种差分均完成实际镜像重建和读回验证；旧整合 ZIP 直接升级已验证。新版已启动并实见 AC 测试战斗，仍以公开测试版发布。

输出 ISO SHA-256：`f7d531fee570817364b2d900585c3e53675423ae76538c0c3608d27c9455679a`。

[完整说明与命令](说明/使用说明.md) · [更新记录](docs/RELEASE_NOTES.md) · [验证记录](RELEASE_VALIDATION.json) · [反馈](https://github.com/AmuroRX-93/acff-ps2-chinese-port/issues)
