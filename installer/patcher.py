"""ACFF PSP Chinese -> PS2 resource port. Python standard library only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

BLOCK = 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(BLOCK), b''):
            h.update(b)
    return h.hexdigest()


def xor_bytes(a, b):
    if len(a) != len(b):
        raise ValueError('差分块长度错误')
    return (int.from_bytes(a, 'little') ^ int.from_bytes(b, 'little')).to_bytes(len(a), 'little')


def apply(source, output, bundle, report=print):
    source, output, bundle = map(Path, (source, output, bundle))
    if output.exists() or output.is_symlink():
        raise ValueError('输出文件已经存在，请另选名称；不会覆盖任何镜像。')
    if source.resolve() == output.resolve():
        raise ValueError('不能覆盖原版镜像。')
    with zipfile.ZipFile(bundle) as z:
        m = json.loads(z.read('manifest.json'))
        if m.get('format') != 'ACFF-XOR-1' or m.get('block_size') != BLOCK:
            raise ValueError('不支持的补丁格式')
        if source.stat().st_size != m['size']:
            raise ValueError('镜像大小不匹配，需要指定版本的 PS2 日版原版 ISO。')
        report('正在核对完整原版镜像，请稍候……')
        if digest(source) != m['source_sha256']:
            raise ValueError('原版 SHA-256 不匹配。不要使用 PSP 版、压缩镜像或其他汉化版。')
        count = (m['size'] + BLOCK - 1) // BLOCK
        chunks = m['chunks']
        if not isinstance(chunks, list) or any(type(i) is not int or not 0 <= i < count for i in chunks) or len(set(chunks)) != len(chunks):
            raise ValueError('差分块索引错误')
        changed = set(chunks)
        for i in changed:
            if z.getinfo(f'blocks/{i:06d}.xor').file_size != min(BLOCK, m['size'] - i * BLOCK):
                raise ValueError('差分块大小错误')
        if shutil.disk_usage(output.parent).free < m['size'] + 64 * BLOCK:
            raise ValueError('输出磁盘空间不足，请至少预留 3.6 GB。')
        report('原版校验通过，正在生成汉化移植版；原版文件保持不变。')
        created = False
        try:
            h = hashlib.sha256()
            with source.open('rb') as src, output.open('xb') as dst:
                created = True
                for i in range(count):
                    b = src.read(BLOCK)
                    if i in changed:
                        b = xor_bytes(b, z.read(f'blocks/{i:06d}.xor'))
                    h.update(b)
                    dst.write(b)
                    if i % 256 == 0:
                        report(f'生成进度：{min(100, (i + 1) * 100 // count)}%')
                dst.flush()
                os.fsync(dst.fileno())
            if h.hexdigest() != m['target_sha256']:
                raise ValueError('输出校验失败，已撤销本次输出。')
            report('正在读回核对输出镜像……')
            if digest(output) != m['target_sha256']:
                raise ValueError('磁盘读回校验失败，已撤销本次输出。')
        except BaseException:
            if created:
                output.unlink(missing_ok=True)
            raise
    report(f'完成：{output}\n请在模拟器中打开新 ISO，从游戏重新开机，不要加载旧即时存档。')


def path_from_input(text):
    value = text.strip()
    direct = Path(value)
    if direct.exists():
        return direct
    if os.name != 'nt':
        import shlex
        try:
            words = shlex.split(value)
            if len(words) == 1:
                return Path(words[0])
        except ValueError:
            pass
    return Path(value.strip('"'))


def choose_source():
    try:
        import tkinter as tk
        from tkinter.filedialog import askopenfilename
    except ImportError:
        tk = None
    if tk is not None:
        root = None
        try:
            root = tk.Tk()
            root.withdraw()
            name = askopenfilename(title='选择 PS2 日版原版 ISO（SLPS-25461）', filetypes=[('PS2 ISO', '*.iso'), ('所有文件', '*')])
            if not name:
                raise KeyboardInterrupt
            return Path(name)
        except tk.TclError:
            pass
        finally:
            if root is not None:
                root.destroy()
    return path_from_input(input('请输入或拖入原版 ISO 的完整路径，再按回车：\n'))


def main():
    print('ACFF — PSP 汉化资源移植至 PS2 | v0.12.4 公开测试版')
    print('原 PSP 汉化：becky / ben / WEFGOD 等；PS2 移植发布：AmuroRX-93')
    if len(sys.argv) > 1:
        source = Path(sys.argv[1])
    else:
        source = choose_source()
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else source.with_name(source.stem + '_PSP汉化移植PS2_v0.12.4.iso')
    bundle = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parent.parent / 'ACFF_PSP_to_PS2_v0.12.4.acpatch'
    apply(source, output, bundle)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。')
        sys.exit(130)
    except Exception as e:
        print(f'\n未完成：{e}', file=sys.stderr)
        sys.exit(1)
