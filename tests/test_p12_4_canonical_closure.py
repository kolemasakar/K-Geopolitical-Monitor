from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_p12_4_gate_remains_canonical_after_later_phase_progress():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md")

    assert "P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED" in roadmap
    assert "P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED" in readme
    assert "P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED" in plan
    assert "P12.5" in roadmap
    assert "P12.5" in readme
    assert "P12.5" in plan


def test_p12_4_preserves_production_storage_and_paid_provider_contracts():
    readme = _read("README.md")
    roadmap = _read("ROADMAP.md")
    result = _read("docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md")

    assert "Production/live operational status: NOT_OPERATIONAL" in readme
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in readme
    assert "Production/live operational status: NOT_OPERATIONAL" in roadmap
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in roadmap
    assert "paid providers: `NONE_APPROVED`" in result


def test_p12_4_language_slice_and_gap_remain_explicit():
    documents = "\n".join(
        [
            _read("README.md"),
            _read("ARCHITECTURE.md"),
            _read("SOURCE_POLICY.md"),
            _read("docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md"),
            _read("docs/implementation/P12_4_CONTROLLED_LIVE_LANGUAGE_SOURCE_MATRIX.md"),
        ]
    )
    for language in ("uk", "ru", "pl", "tr"):
        assert language in documents
    assert "not global language coverage" in documents.lower()


def test_p12_4_translation_and_origin_boundaries_remain_explicit():
    readme = _read("README.md")
    source_policy = _read("SOURCE_POLICY.md")
    result = _read("docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md")

    assert "translation remains a separate derived representation" in readme.lower()
    assert "media/domain/language/adapter/item count is not independent-origin count" in source_policy
    assert "media/domain/language/adapter/item count is not independent-origin count" in result
    assert "does not directly promote factual verification" in result
