"""ACFF movie upgrade: Python 3.8+, standard library; v0.12.14 ONLY."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

BLOCK = 1024 * 1024
SOURCE = 'f7d531fee570817364b2d900585c3e53675423ae76538c0c3608d27c9455679a'
TARGET = '01fa52626eca140ae22e82f6830a8cd886ad24977eaa9c1883bebc281888c923'
SIZE = 3470426112

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(BLOCK), b''): h.update(b)
    return h.hexdigest()

def xor_bytes(a,b):
    if len(a)!=len(b): raise ValueError('差分块长度错误')
    return (int.from_bytes(a,'little')^int.from_bytes(b,'little')).to_bytes(len(a),'little')

def apply(source, output, bundle, report=print):
    source,output,bundle = map(Path,(source,output,bundle))
    partial=output.with_name(output.name+'.partial')
    if output.exists() or output.is_symlink(): raise ValueError('目标已存在；不会覆盖。请另选输出文件名。')
    if partial.exists() or partial.is_symlink(): raise ValueError('存在上次未完成的 .partial 文件，请先另选输出名称。')
    if source.resolve()==output.resolve(): raise ValueError('不能覆盖输入镜像。')
    if source.stat().st_size!=SIZE: raise ValueError('镜像大小不符：只支持 v0.12.14 汉化 ISO，不支持 ZIP、原版或 v0.12.6。')
    report('正在核对 v0.12.14 完整镜像……',flush=True) if report is print else report('正在核对 v0.12.14 完整镜像……')
    if digest(source)!=SOURCE: raise ValueError('输入 SHA-256 不匹配：必须使用未修改的 v0.12.14 汉化 ISO。')
    with zipfile.ZipFile(bundle) as z:
        m=json.loads(z.read('manifest.json'))
        if (m.get('format'),m.get('block_size'),m.get('source_sha256'),m.get('target_sha256'),m.get('size'),m.get('source_version')) != ('ACFF-XOR-1',BLOCK,SOURCE,TARGET,SIZE,'0.12.14'):
            raise ValueError('补丁版本或指纹不匹配。')
        count=(SIZE+BLOCK-1)//BLOCK
        chunks=m.get('chunks')
        if not isinstance(chunks,list) or any(type(i) is not int or not 0<=i<count for i in chunks) or len(set(chunks))!=len(chunks): raise ValueError('差分索引无效。')
        expected={'manifest.json'}|{f'blocks/{i:06d}.xor' for i in chunks}
        if len(z.infolist())!=len(expected) or set(z.namelist())!=expected: raise ValueError('差分内容不完整或重复。')
        for i in chunks:
            if z.getinfo(f'blocks/{i:06d}.xor').file_size!=min(BLOCK,SIZE-i*BLOCK): raise ValueError('差分块大小无效。')
        if shutil.disk_usage(output.parent).free<SIZE+64*BLOCK: raise ValueError('空间不足，请在输出磁盘保留至少 3.6 GB 可用空间。')
        changed=set(chunks); created=False; committed=False
        try:
            with source.open('rb') as src,partial.open('xb') as dst:
                created=True; h=hashlib.sha256()
                for i in range(count):
                    b=src.read(min(BLOCK,SIZE-i*BLOCK))
                    if len(b)!=min(BLOCK,SIZE-i*BLOCK): raise ValueError('输入文件在处理期间发生变化。')
                    if i in changed: b=xor_bytes(b,z.read(f'blocks/{i:06d}.xor'))
                    h.update(b); dst.write(b)
                    if i%256==0: report(f'生成进度：{(i+1)*100//count}%')
                dst.flush(); os.fsync(dst.fileno())
            if h.hexdigest()!=TARGET: raise ValueError('输出 SHA-256 不匹配。')
            report('读回核对新镜像……')
            if digest(partial)!=TARGET: raise ValueError('读回校验失败。')
            # Atomic commit without replacing a concurrent/new existing output.
            if os.name=='nt': os.rename(partial,output)
            else:
                os.link(partial,output)
                partial.unlink()
            committed=True
        except BaseException:
            if created and not committed: partial.unlink(missing_ok=True)
            raise
    report(f'完成：{output}\n原 ISO 保留。请冷启动新 ISO 并读取游戏内存档，不要载入旧即时存档。')
    return output

def choose():
    try:
        import tkinter as tk
        from tkinter.filedialog import askopenfilename
        root=tk.Tk(); root.withdraw()
        try: name=askopenfilename(title='选择 v0.12.14 汉化 ISO',filetypes=[('ISO','*.iso')])
        finally: root.destroy()
        if not name: raise KeyboardInterrupt
        return Path(name)
    except (ImportError, RuntimeError): pass
    except Exception as e:
        if e.__class__.__name__!='TclError': raise
    value=input('拖入 v0.12.14 汉化 ISO 路径，然后回车：\n').strip()
    if os.name!='nt':
        import shlex
        parts=shlex.split(value)
        if len(parts)==1: value=parts[0]
    return Path(value.strip('"'))

def main():
    p=argparse.ArgumentParser(description='仅从 v0.12.14 升级为 ACFF v0.13.0 影片汉化测试版')
    p.add_argument('source',nargs='?');p.add_argument('output',nargs='?')
    args=p.parse_args()
    source=Path(args.source) if args.source else choose()
    output=Path(args.output) if args.output else source.with_name('ACFF_PS2_v0.13.0_movies.iso')
    apply(source,output,Path(__file__).resolve().parent/'movie_patch.zip')
if __name__=='__main__':
    try: main()
    except KeyboardInterrupt:
        print('\n已取消；原镜像不受影响。');sys.exit(130)
    except Exception as e:
        print(f'\n未完成：{e}',file=sys.stderr);sys.exit(1)
