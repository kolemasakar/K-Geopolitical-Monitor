"""Offline validation of bounded KGM read-only metrics without host mutation."""
import importlib.util, unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]/"ops/p24_observability/kgm_readonly_metrics.py"
s=importlib.util.spec_from_file_location("metrics",P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class MetricsTests(unittest.TestCase):
 def test_normal_and_no_sensitive_contents(self):
  def fake(*args):
   if args[1:3]==("show","kgm-monitor.service"):
    return "ActiveState=active\nNRestarts=0\nMemoryCurrent=1000\nMemoryPeak=2000"
   return None
  class Fs: f_bavail=80;f_blocks=100
  with patch.object(m,"cmd",side_effect=fake),patch.object(m.os,"statvfs",return_value=Fs()):
   o=m.measure()
  self.assertEqual(o["state"],"PASS")
  self.assertIsNone(o["memory_events"])
  self.assertNotIn("journal",str(o))
 def test_low_disk(self):
  class Fs: f_bavail=5;f_blocks=100
  with patch.object(m,"cmd",return_value="ActiveState=active"),patch.object(m.os,"statvfs",return_value=Fs()):
   self.assertEqual(m.measure()["state"],"ALERT")
 def test_failed_service(self):
  class Fs: f_bavail=95;f_blocks=100
  with patch.object(m,"cmd",return_value="ActiveState=failed"),patch.object(m.os,"statvfs",return_value=Fs()):
   self.assertEqual(m.measure()["state"],"ALERT")
if __name__=="__main__":unittest.main()
