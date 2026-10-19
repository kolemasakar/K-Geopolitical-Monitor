"""Review gate: no production deletion and fail-closed approvals."""
import importlib.util
import unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"ops/p24_diag/kgm-p24-cleanup-executor-review.py"
spec=importlib.util.spec_from_file_location("executor_review",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class ExecutorReviewTests(unittest.TestCase):
 def setUp(self):
  self.pre={"status":"PREFLIGHT_PASS","deletion_performed":False,
            "files":{k:{} for k in m.TARGETS[:4]},"digest":"abc"}
  self.ap={"decision":m.APPROVAL_LITERAL,"targets":list(m.TARGETS),"preflight_digest":"abc"}
 def test_review_only(self):
  v=m.decision("/tmp/isolated-cleanup-fixture",self.pre,self.ap)
  self.assertFalse(v["deletion_performed"])
  self.assertEqual(v["status"],"REVIEW_ONLY")
 def test_block_production(self):
  with self.assertRaisesRegex(ValueError,"production_executor_not_implemented"):
   m.decision("/var/lib",self.pre,self.ap)
 def test_no_owner_approval(self):
  self.ap["decision"]="PENDING"
  with self.assertRaises(ValueError):m.decision("/tmp/isolated-cleanup-fixture",self.pre,self.ap)
 def test_stale_preflight(self):
  self.ap["preflight_digest"]="other"
  with self.assertRaises(ValueError):m.decision("/tmp/isolated-cleanup-fixture",self.pre,self.ap)
 def test_extra_target(self):
  self.ap["targets"].append("/etc/passwd")
  with self.assertRaises(ValueError):m.decision("/tmp/isolated-cleanup-fixture",self.pre,self.ap)
 def test_missing_target(self):
  self.pre["files"].pop(m.TARGETS[0])
  with self.assertRaises(ValueError):m.decision("/tmp/isolated-cleanup-fixture",self.pre,self.ap)
if __name__=="__main__":unittest.main()
