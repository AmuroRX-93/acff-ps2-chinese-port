import hashlib,importlib.util,json,tempfile,unittest,zipfile
from pathlib import Path
s=importlib.util.spec_from_file_location('manage',Path(__file__).resolve().parents[1]/'installer/manage.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class InstallerTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name)
  self.old=b'abcdefgh'*16384;self.new=b'ABCDEFGH'*16384;m.TARGET_SIZE=len(self.new);m.TARGET_HASH=hashlib.sha256(self.new).hexdigest()
  self.iso=self.p/'old.iso';self.iso.write_bytes(self.old);self.out=self.p/'new.iso'
  self.bundle=self.p/'test.acpatch'
  with zipfile.ZipFile(self.bundle,'w') as z:
   z.writestr('blocks/000000.xor',m.xor_bytes(self.old,self.new));z.writestr('manifest.json',json.dumps(dict(format='ACFF-XOR-1',block_size=m.BLOCK,size=len(self.old),source_sha256=hashlib.sha256(self.old).hexdigest(),target_sha256=m.TARGET_HASH,chunks=[0])))
 def tearDown(self):self.t.cleanup()
 def test_iso_upgrade(self):
  m.patch(self.iso,self.out,self.p,lambda _:None);self.assertEqual(self.out.read_bytes(),self.new);self.assertEqual(self.iso.read_bytes(),self.old)
 def test_old_integration_zip(self):
  p=self.p/'旧整合 包.zip'
  with zipfile.ZipFile(p,'w') as z:z.writestr('包/游戏.iso',self.old)
  m.patch(p,self.out,self.p,lambda _:None);self.assertEqual(self.out.read_bytes(),self.new)
 def test_refuses_overwrite(self):
  self.out.write_bytes(b'KEEP')
  with self.assertRaises(ValueError):m.patch(self.iso,self.out,self.p,lambda _:None)
  self.assertEqual(self.out.read_bytes(),b'KEEP')
 def test_refuses_wrong_source(self):
  self.iso.write_bytes(b'x'*len(self.old))
  with self.assertRaises(ValueError):m.patch(self.iso,self.out,self.p,lambda _:None)
  self.assertFalse(self.out.exists())
 def test_corruption_cleans_output(self):
  with zipfile.ZipFile(self.bundle,'a') as z:
   # Corrupt payload without invalidating ZIP CRC: final target hash must catch it.
   meta=json.loads(z.read('manifest.json'))
  with zipfile.ZipFile(self.bundle,'w') as z:
   z.writestr('manifest.json',json.dumps(meta));z.writestr('blocks/000000.xor',b'x'*len(self.old))
  with self.assertRaises(ValueError):m.patch(self.iso,self.out,self.p,lambda _:None)
  self.assertFalse(self.out.exists());self.assertEqual(self.iso.read_bytes(),self.old)
 def test_ambiguous_zip_refused(self):
  p=self.p/'two.zip'
  with zipfile.ZipFile(p,'w') as z:z.writestr('a.iso',self.old);z.writestr('b.iso',self.old)
  with self.assertRaises(ValueError):m.patch(p,self.out,self.p,lambda _:None)
 def test_installs_bundled_iso(self):
  m.ROOT=self.p;(self.p/m.ISO_NAME).write_bytes(self.new);folder=self.p/'games';folder.mkdir()
  m.install(folder,lambda _:None);self.assertEqual((folder/m.ISO_NAME).read_bytes(),self.new)
 def test_already_current(self):
  self.iso.write_bytes(self.new);self.assertEqual(m.patch(self.iso,self.out,self.p,lambda _:None),self.iso);self.assertFalse(self.out.exists())
if __name__=='__main__':unittest.main()
