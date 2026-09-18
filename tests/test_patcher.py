import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'installer'), str(Path(__file__).resolve().parents[1] / 'tools')]
from patcher import apply, BLOCK, path_from_input
from build_patch import build

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source.iso'
        self.target = self.root / 'target.iso'
        self.patch = self.root / 'patch.acpatch'
        self.out = self.root / 'out.iso'
        self.original = b'A' * BLOCK + b'B' * BLOCK + b'end'
        self.expected = b'C' + self.original[1:-3] + b'fin'
        self.source.write_bytes(self.original)
        self.target.write_bytes(self.expected)
        self.manifest = build(self.source, self.target, self.patch)
    def run_patch(self):
        apply(self.source, self.out, self.patch, report=lambda _: None)
    def test_mac_dragged_path_with_spaces(self):
        self.assertEqual(path_from_input("/tmp/game\\ image.iso"), Path("/tmp/game image.iso"))
    def test_changed_and_unchanged_blocks_round_trip(self):
        self.assertEqual(self.manifest['chunks'], [0, 2])
        self.run_patch()
        self.assertEqual(self.out.read_bytes(), self.expected)
        self.assertEqual(self.source.read_bytes(), self.original)
    def test_wrong_source_same_size(self):
        self.source.write_bytes(b'X' + self.original[1:])
        with self.assertRaisesRegex(ValueError, 'SHA-256'): self.run_patch()
        self.assertFalse(self.out.exists())
    def test_never_overwrites_existing_output(self):
        self.out.write_bytes(b'precious')
        with self.assertRaises(ValueError): self.run_patch()
        self.assertEqual(self.out.read_bytes(), b'precious')
    def test_corrupt_delta_removes_incomplete_output(self):
        bad = self.root / 'corrupt.acpatch'
        with zipfile.ZipFile(self.patch) as src, zipfile.ZipFile(bad, 'w') as dst:
            for info in src.infolist():
                b = src.read(info.filename)
                if info.filename == 'blocks/000000.xor': b = bytes([b[0] ^ 1]) + b[1:]
                dst.writestr(info.filename, b)
        self.patch = bad
        with self.assertRaisesRegex(ValueError, '输出校验'): self.run_patch()
        self.assertFalse(self.out.exists())
        self.assertEqual(self.source.read_bytes(), self.original)
    def test_interruption_removes_incomplete_output(self):
        def interrupt(text):
            if text.startswith('生成进度'): raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt): apply(self.source, self.out, self.patch, report=interrupt)
        self.assertFalse(self.out.exists())
        self.assertEqual(self.source.read_bytes(), self.original)

if __name__ == '__main__': unittest.main()
