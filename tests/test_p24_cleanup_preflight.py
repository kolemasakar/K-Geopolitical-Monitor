"""Isolated no-delete preflight tests. Run: python3 -m unittest discover -s tests -p 'test_p24_cleanup_preflight.py'"""
import hashlib, importlib.util, json, os, tempfile, unittest
from pathlib import Path
M=Path(__file__).resolve().parents[1]/"ops/p24_diag/kgm-p24-cleanup-preflight.py"
spec=importlib.util.spec_from_file_location("preflight",M); p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  for d in p.PARENTS+p.DIRS:(self.root/d).mkdir(parents=True,exist_ok=True)
  self.backup=b"valid-backup";self.manifest=json.dumps({"sha256":hashlib.sha256(self.backup).hexdigest(),"size":len(self.backup)}).encode();self.report=b"report"
  for f,b in zip(p.FILES,(self.backup,self.backup,self.manifest,self.report)):(self.root/f).write_bytes(b)
  self.ev={"backup_sha256":hashlib.sha256(self.backup).hexdigest(),"backup_size":len(self.backup),"manifest_sha256":hashlib.sha256(self.manifest).hexdigest(),"report_sha256":hashlib.sha256(self.report).hexdigest()}
  self.uid=os.getuid()
 def check(self):return p.inspect(self.root,self.ev,self.uid)
 def test_good(self):self.assertEqual(len(self.check()),4)
 def test_bad_hash(self):
  (self.root/p.FILES[0]).write_bytes(b"bad")
  with self.assertRaises(ValueError):self.check()
 def test_extra_entry(self):
  (self.root/p.DIRS[1]/"unexpected").touch()
  with self.assertRaises(ValueError):self.check()
 def test_symlink(self):
  f=self.root/p.FILES[2];f.unlink();f.symlink_to(self.root/p.FILES[3])
  with self.assertRaises(ValueError):self.check()
 def test_hardlink(self):
  os.link(self.root/p.FILES[0],self.root/"extra-link")
  with self.assertRaises(ValueError):self.check()
 def test_missing(self):
  (self.root/p.FILES[0]).unlink()
  with self.assertRaises(ValueError):self.check()
 def test_wrong_owner(self):
  with self.assertRaises(ValueError):p.inspect(self.root,self.ev,self.uid+100000)
if __name__=="__main__":unittest.main()
