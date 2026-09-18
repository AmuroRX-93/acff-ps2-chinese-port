"""Build changed-block XOR bundle; does not publish game files."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'installer'))
from patcher import BLOCK, xor_bytes


def build(source, target, output):
    source, target = Path(source), Path(target)
    if source.stat().st_size != target.stat().st_size:
        raise ValueError('This format requires equal-sized images')
    a_hash, b_hash = hashlib.sha256(), hashlib.sha256()
    changed = []
    with source.open('rb') as a, target.open('rb') as b, zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        i = 0
        while True:
            x, y = a.read(BLOCK), b.read(BLOCK)
            if not x:
                break
            a_hash.update(x)
            b_hash.update(y)
            if x != y:
                changed.append(i)
                z.writestr(f'blocks/{i:06d}.xor', xor_bytes(x, y))
            i += 1
        m = dict(format='ACFF-XOR-1', version='0.12.4', game='SLPS-25461', size=source.stat().st_size, block_size=BLOCK, source_sha256=a_hash.hexdigest(), target_sha256=b_hash.hexdigest(), chunks=changed)
        z.writestr('manifest.json', json.dumps(m, indent=2))
    return m


if __name__ == '__main__':
    print(json.dumps(build(*sys.argv[1:]), indent=2))
