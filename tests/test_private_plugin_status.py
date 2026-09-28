"""Synthetic, offline contract tests for the owner-only status projection."""
import unittest

from kgeopolitical_monitor.private_plugin_status import kgm_get_status


class FakeReader:
    def state_summary(self):
        return {
            "active_monitoring_watches": 2,
            "last_monitoring_cycle": {
                "run_id": "test-run",
                "status": "DONE",
                "started_at": "2026-09-25T00:00:00Z",
                "completed_at": "2026-09-25T00:01:00Z",
                "error": "SENSITIVE_DO_NOT_EXPOSE",
            },
            "last_unattended_cycle_at": None,
            "unattended_cycle_instrumentation": "NOT_INSTRUMENTED",
            "owner_token": "SENSITIVE_DO_NOT_EXPOSE",
        }

    def degraded_sources(self):
        return [
            {
                "source_id": f"source-{i}",
                "availability_state": "STALE",
                "observed_at": None,
                "error": "SENSITIVE_DO_NOT_EXPOSE",
            }
            for i in range(23)
        ]


class PluginStatusTests(unittest.TestCase):
    def test_projection_is_bounded_and_redacted(self):
        result = kgm_get_status(FakeReader())
        self.assertEqual(result["active_monitoring_watches"], 2)
        self.assertEqual(len(result["degraded_sources"]), 20)
        self.assertTrue(result["degraded_sources_truncated"])
        self.assertNotIn("SENSITIVE_DO_NOT_EXPOSE", repr(result))
        self.assertNotIn("owner_token", repr(result))

    def test_no_inferred_continuity(self):
        result = kgm_get_status(FakeReader())
        self.assertIsNone(result["last_unattended_cycle_at"])
        self.assertEqual(result["acquisition_continuity"], "NOT_VERIFIED")
        self.assertEqual(result["service_health"], "NOT_MEASURED")

    def test_invalid_summary_fails_closed(self):
        class BadReader(FakeReader):
            def state_summary(self):
                return None
        with self.assertRaises(ValueError):
            kgm_get_status(BadReader())

    def test_adversarial_allowed_values_are_dropped(self):
        class MaliciousReader(FakeReader):
            def state_summary(self):
                return {
                    "active_monitoring_watches": True,
                    "last_monitoring_cycle": {
                        "run_id": "secret=abc / invalid",
                        "status": "ok\\nsecret",
                        "started_at": "not a date",
                        "completed_at": None,
                    },
                    "last_unattended_cycle_at": "token=secret",
                    "unattended_cycle_instrumentation": "secret=abc",
                }

            def degraded_sources(self):
                return [{
                    "source_id": "token=secret",
                    "availability_state": "STALE\\nsecret",
                    "observed_at": "bad timestamp",
                }]
        result = kgm_get_status(MaliciousReader())
        self.assertIsNone(result["active_monitoring_watches"])
        self.assertIsNone(result["last_monitoring_cycle"]["run_id"])
        self.assertIsNone(result["last_unattended_cycle_at"])
        self.assertEqual(result["unattended_cycle_instrumentation"], "UNKNOWN")
        self.assertEqual(result["degraded_sources"][0]["source_id"], None)
        self.assertNotIn("secret", repr(result))

    def test_rejects_invalid_degraded_container(self):
        class BadReader(FakeReader):
            def degraded_sources(self):
                return {"unbounded": True}
        with self.assertRaises(ValueError):
            kgm_get_status(BadReader())

    def test_valid_timestamp_and_count(self):
        result = kgm_get_status(FakeReader())
        self.assertEqual(result["last_monitoring_cycle"]["started_at"], "2026-09-25T00:00:00Z")
        self.assertEqual(result["active_monitoring_watches"], 2)


if __name__ == "__main__":
    unittest.main()
