import tempfile, json, zipfile, hashlib, importlib.util, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('upgrade',Path(__file__).with_name('movie_upgrade.py'))
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix='ACFF 中文 空格 '); self.r=Path(self.t.name)
  self.a=self.r/'原版.iso';self.b=self.r/'升级.iso';self.z=self.r/'patch.zip'
  self.data=b'0'*(u.BLOCK+77);self.new=b'1'*u.BLOCK+b'0'*77
  self.a.write_bytes(self.data)
  self.p=patch.multiple(u,SOURCE=hashlib.sha256(self.data).hexdigest(),TARGET=hashlib.sha256(self.new).hexdigest(),SIZE=len(self.data));self.p.start()
  self.man=dict(format='ACFF-XOR-1',block_size=u.BLOCK,size=u.SIZE,source_sha256=u.SOURCE,target_sha256=u.TARGET,source_version='0.12.14',chunks=[0])
  self.bundle()
 def tearDown(self):self.p.stop();self.t.cleanup()
 def bundle(self,bad=False):
  with zipfile.ZipFile(self.z,'w') as z:
   z.writestr('manifest.json',json.dumps(self.man));z.writestr('blocks/000000.xor',b'x'*u.BLOCK if bad else u.xor_bytes(self.data[:u.BLOCK],self.new[:u.BLOCK]))
 def run_apply(self,**kw):return u.apply(self.a,self.b,self.z,kw.get('report',lambda x:None))
 def test_success_chinese_space_and_repeat(self):
  self.run_apply();self.assertEqual(self.b.read_bytes(),self.new);self.assertEqual(self.a.read_bytes(),self.data)
  with self.assertRaises(ValueError):self.run_apply()
 def test_wrong_size(self):
  self.a.write_bytes(b'wrong')
  with self.assertRaises(ValueError):self.run_apply()
  self.assertFalse(self.b.exists())
 def test_wrong_hash(self):
  self.a.write_bytes(b'2'*len(self.data))
  with self.assertRaises(ValueError):self.run_apply()
 def test_wrong_version(self):
  self.man['source_version']='0.12.6';self.bundle()
  with self.assertRaises(ValueError):self.run_apply()
 def test_corrupt_patch(self):
  self.bundle(True)
  with self.assertRaises(ValueError):self.run_apply()
  self.assertFalse(self.b.exists());self.assertFalse(Path(str(self.b)+'.partial').exists())
 def test_interruption(self):
  def report(s):
   if s.startswith('生成进度'):raise KeyboardInterrupt()
  with self.assertRaises(KeyboardInterrupt):self.run_apply(report=report)
  self.assertFalse(self.b.exists());self.assertFalse(Path(str(self.b)+'.partial').exists());self.assertEqual(self.a.read_bytes(),self.data)
 def test_insufficient_space(self):
  with patch.object(u.shutil,'disk_usage',return_value=type('Usage',(),{'free':0})()):
   with self.assertRaises(ValueError):self.run_apply()
 def test_readonly_output(self):
  original=Path.open
  def op(p,*args,**kwargs):
   if p.name.endswith('.partial'):raise PermissionError('read-only fixture')
   return original(p,*args,**kwargs)
  with patch.object(Path,'open',op):
   with self.assertRaises(PermissionError):self.run_apply()
  self.assertFalse(self.b.exists());self.assertEqual(self.a.read_bytes(),self.data)
 def test_concurrent_output(self):
  def report(s):
   if s.startswith('读回'):self.b.write_bytes(b'do not overwrite')
  with self.assertRaises(FileExistsError):self.run_apply(report=report)
  self.assertEqual(self.b.read_bytes(),b'do not overwrite')
 def test_previous_partial(self):
  p=Path(str(self.b)+'.partial');p.write_bytes(b'previous')
  with self.assertRaises(ValueError):self.run_apply()
  self.assertEqual(p.read_bytes(),b'previous')
if __name__=='__main__':unittest.main(verbosity=2)
