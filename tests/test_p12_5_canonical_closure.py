from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_p12_5_gate_and_later_phase_progress_are_canonical():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md")
    result = _read("docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md")

    for document in (roadmap, readme, plan, result):
        assert "P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED" in document

    # Historical P12.5 closure must remain valid after the validated P12.6 gate.
    assert "PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED" in roadmap
    assert "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE / NEXT_NOT_STARTED" in roadmap
    assert "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE / NEXT_NOT_STARTED" in readme
    assert "P12.6 — Phase 12 Validation Matrix" in plan
    assert "State: `VALIDATED`" in plan


def test_p12_5_measured_degradation_remains_explicit():
    matrix = _read("docs/implementation/P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md")
    result = _read("docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md")

    assert "governed source paths: `10`" in result
    assert "measured source paths: `10`" in result
    assert "unmeasured: `0`" in result
    assert "8 SUCCESS / 2 FAILED" in result
    assert "European Parliament Press Releases" in matrix
    assert "UNAVAILABLE" in matrix
    assert "PARSER" in matrix
    assert "Haberturk News" in matrix
    assert "original_url must be HTTP or HTTPS" in matrix
    assert "OSCE Latest News" in matrix
    assert "STALE" in matrix
    assert "governed portfolio state remains `ACTIVE`" in result


def test_p12_5_egress_inventory_is_factual_not_deployed_policy():
    matrix = _read("docs/implementation/P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md")
    result = _read("docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md")
    security = _read("SECURITY_AND_DATA_POLICY.md")

    for hostname in (
        "api.gdeltproject.org",
        "ec.europa.eu",
        "feeds.osce.org",
        "meduza.io",
        "rss.haberturk.com",
        "www.consilium.europa.eu",
        "www.europarl.europa.eu",
        "www.gov.uk",
        "www.pravda.com.ua",
        "www.rmf24.pl",
    ):
        assert hostname in matrix
    assert "not an outbound firewall rule" in matrix.lower()
    assert "does not deploy an outbound allowlist" in result.lower()
    assert "broad outbound egress" in security.lower()


def test_p12_5_preserves_truth_storage_and_production_boundaries():
    readme = _read("README.md")
    roadmap = _read("ROADMAP.md")
    result = _read("docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md")

    assert "Production/live operational status: NOT_OPERATIONAL" in readme
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in readme
    assert "Production/live operational status: NOT_OPERATIONAL" in roadmap
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in roadmap
    assert "operational health does not change claim truth" in result
    assert "source/host/language/item count does not create independent-origin count" in result
    assert "paid providers: `NONE_APPROVED`" in result
