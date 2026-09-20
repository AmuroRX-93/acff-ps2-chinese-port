"""ACFF portable installer/update manager; Python 3.10+, standard library only."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if ROOT.name == '工具':
    ROOT = ROOT.parent
BLOCK = 1024 * 1024
VERSION = '0.12.14'
ISO_NAME = 'ACFF_PS2_PSP_Chinese_Port_v0.12.14.iso'
TARGET_HASH = 'f7d531fee570817364b2d900585c3e53675423ae76538c0c3608d27c9455679a'
TARGET_SIZE = 3470426112


def bundled_iso():
    root_image = ROOT / ISO_NAME
    return root_image if root_image.is_file() else ROOT / '游戏' / ISO_NAME


def digest_stream(stream):
    h = hashlib.sha256()
    for b in iter(lambda: stream.read(8 * BLOCK), b''):
        h.update(b)
    return h.hexdigest()


@contextlib.contextmanager
def image_stream(path):
    """Read a normal ISO or the sole ISO in an older integration ZIP."""
    path = Path(path)
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as z:
            entries = [x for x in z.infolist() if x.filename.lower().endswith('.iso')
                       and not Path(x.filename).name.startswith('._') and not x.is_dir()]
            if len(entries) != 1:
                raise ValueError('ZIP 中必须只有一个游戏 ISO；请解压后单独选择需要升级的 ISO。')
            with z.open(entries[0]) as f:
                yield f, entries[0].file_size
    else:
        with path.open('rb') as f:
            yield f, path.stat().st_size


def image_digest(path):
    with image_stream(path) as (f, size):
        return size, digest_stream(f)


def normalize_source(path):
    p = Path(path).expanduser()
    if p.is_dir():
        matches = [x for x in p.rglob('*') if x.is_file() and x.suffix.lower() == '.iso'
                   and not x.name.startswith('._')]
        if len(matches) != 1:
            raise ValueError('文件夹中没有唯一的 ISO，请直接选择其中要处理的 ISO 文件。')
        p = matches[0]
    if not p.is_file():
        raise ValueError('找不到输入文件。')
    return p


def parse_path(s):
    s = s.strip()
    if Path(s).exists():
        return Path(s)
    if os.name != 'nt':
        try:
            parts = shlex.split(s)
            if len(parts) == 1:
                return Path(parts[0])
        except ValueError:
            pass
    return Path(s.strip('"'))


def choose(title, directory=False):
    root = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        value = (filedialog.askdirectory(title=title) if directory else
                 filedialog.askopenfilename(title=title, filetypes=[('ISO 或旧整合 ZIP', '*.iso *.zip'), ('所有文件', '*')]))
        if not value:
            raise KeyboardInterrupt
        return Path(value)
    except (ImportError, RuntimeError):
        pass
    except Exception as e:
        if type(e).__name__ != 'TclError':
            raise
    finally:
        if root is not None:
            root.destroy()
    return parse_path(input(title + '\n可拖入路径，然后按回车：\n'))


def xor_bytes(a, b):
    if len(a) != len(b):
        raise ValueError('差分块长度错误。')
    return (int.from_bytes(a, 'little') ^ int.from_bytes(b, 'little')).to_bytes(len(a), 'little')


def write_verified(source, output, target_size, target_hash, transform=None, report=print):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('输出已存在，未覆盖。请选择其他输出名称，或使用“校验镜像”检查已有文件。')
    if not output.parent.is_dir():
        raise ValueError('输出文件夹不存在。')
    if shutil.disk_usage(output.parent).free < target_size + 64 * BLOCK:
        raise ValueError('空间不足：输出位置请至少预留 3.6 GB。')
    created = False
    try:
        with image_stream(source) as (src, size):
            if size != target_size:
                raise ValueError('镜像大小不匹配。')
            with output.open('xb') as dst:
                created = True
                h = hashlib.sha256()
                count = (size + BLOCK - 1) // BLOCK
                for i in range(count):
                    b = src.read(min(BLOCK, size - i * BLOCK))
                    if len(b) != min(BLOCK, size - i * BLOCK):
                        raise ValueError('输入文件提前结束。')
                    if transform:
                        b = transform(i, b)
                    dst.write(b)
                    h.update(b)
                    if i % 256 == 0:
                        report(f'生成进度：{(i + 1) * 100 // count}%')
                if src.read(1):
                    raise ValueError('输入长度超出预期。')
                dst.flush()
                os.fsync(dst.fileno())
        if h.hexdigest() != target_hash:
            raise ValueError('生成结果校验不通过。')
        report('正在读回校验新镜像……')
        if image_digest(output) != (target_size, target_hash):
            raise ValueError('磁盘读回校验不通过。')
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    report(f'完成：{output}\n请在模拟器中打开此新 ISO，冷启动后读取原来的游戏内记忆卡存档。')
    return output


def patch(source, output=None, patch_dir=ROOT, report=print):
    source = normalize_source(source)
    report('正在识别并校验输入版本……')
    size, sha = image_digest(source)
    if (size, sha) == (TARGET_SIZE, TARGET_HASH):
        report('该镜像已经是本次 v0.12.14，不需要重复升级。')
        return source
    matches = []
    for p in sorted(Path(patch_dir).rglob('*.acpatch')):
        with zipfile.ZipFile(p) as z:
            m = json.loads(z.read('manifest.json'))
        if m.get('source_sha256') == sha and m.get('size') == size:
            matches.append((p, m))
    if len(matches) != 1:
        raise ValueError('未找到与该镜像匹配的补丁。本版支持 PS2 日版原版和公开 v0.12.6；请下载对应完整差分包／v0.12.6 升级包。不要使用 PSP、CHD/CSO 或其他候选版。')
    p, m = matches[0]
    if m.get('format') != 'ACFF-XOR-1' or m.get('block_size') != BLOCK or m.get('target_sha256') != TARGET_HASH or m.get('size') != TARGET_SIZE:
        raise ValueError('差分元数据不匹配。')
    count = (size + BLOCK - 1) // BLOCK
    chunks = m.get('chunks')
    if not isinstance(chunks, list) or any(type(i) is not int or not 0 <= i < count for i in chunks) or len(chunks) != len(set(chunks)):
        raise ValueError('差分块索引错误。')
    changed = set(chunks)
    output = Path(output) if output else source.parent / ISO_NAME
    with zipfile.ZipFile(p) as z:
        for i in changed:
            if z.getinfo(f'blocks/{i:06d}.xor').file_size != min(BLOCK, size - i * BLOCK):
                raise ValueError('差分块大小错误。')
        report('版本校验通过，生成新镜像；原镜像、旧压缩包和存档保持不变。')
        return write_verified(source, output, size, TARGET_HASH,
                              lambda i, b: xor_bytes(b, z.read(f'blocks/{i:06d}.xor')) if i in changed else b, report)


def install(folder, report=print):
    source = bundled_iso()
    if not source.is_file():
        raise ValueError('这个是差分包。请使用“一键汉化或升级”，选择自己的 ISO 或旧整合 ZIP。')
    report('正在校验整合包中的镜像……')
    if image_digest(source) != (TARGET_SIZE, TARGET_HASH):
        raise ValueError('整合镜像校验失败，请重新解压或下载。')
    return write_verified(source, Path(folder) / ISO_NAME, TARGET_SIZE, TARGET_HASH, report=report)


def main():
    p = argparse.ArgumentParser(description='ACFF PSP 汉化资源移植至 PS2 — v0.12.14 安装与升级工具')
    p.add_argument('action', choices=['patch', 'install', 'verify', 'start'])
    p.add_argument('source', nargs='?')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    print('PSP 原汉化：becky / ben / WEFGOD 等；PS2 移植：AmuroRX-93')
    if a.action == 'start':
        iso = bundled_iso()
        if not iso.is_file():
            raise ValueError('请先升级生成新 ISO，再从模拟器打开。')
        if sys.platform == 'darwin':
            for app in [Path('/Applications/ARMSX2.app'),Path.home()/'Applications/ARMSX2.app',Path('/Applications/PCSX2.app'),Path.home()/'Applications/PCSX2.app']:
                if app.is_dir():
                    subprocess.run(['open','-a',str(app),'--args','--',str(iso)],check=True)
                    return
        candidates = [p for d in [ROOT/'模拟器',Path(os.environ.get('ProgramFiles','C:/Program Files'))/'PCSX2',Path(os.environ.get('LOCALAPPDATA','C:/Users/Default/AppData/Local'))/'Programs/PCSX2'] if d.is_dir() for p in d.glob('pcsx2*.exe')]
        exe = candidates[0] if len(candidates)==1 else parse_path(input('请拖入自己的 PS2 模拟器可执行文件，按回车：\n'))
        if not exe.is_file():
            raise ValueError('找不到模拟器。也可以直接从模拟器打开“游戏”文件夹中的 ISO。')
        subprocess.Popen([str(exe),'--',str(iso)])
    elif a.action == 'patch':
        patch(a.source or choose('选择 PS2 原版、v0.12.6 ISO，或旧整合包 ZIP'), a.output)
    elif a.action == 'install':
        install(Path(a.source) if a.source else choose('选择游戏镜像目录（原有游戏保持不变）', True))
    else:
        source = normalize_source(a.source or (bundled_iso() if bundled_iso().exists() else choose('选择要校验的 v0.12.14 ISO 或整合 ZIP')))
        if image_digest(source) != (TARGET_SIZE, TARGET_HASH):
            raise ValueError('不是本次 v0.12.14 的完整镜像。')
        print(f'校验通过：{source}\nSHA-256：{TARGET_HASH}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消，本次未完成输出已清理。')
        sys.exit(130)
    except Exception as e:
        print(f'\n未完成：{e}', file=sys.stderr)
        sys.exit(1)
