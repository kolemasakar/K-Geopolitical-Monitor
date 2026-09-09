import pytest

from kgeopolitical_monitor.shared_runtime_postgres_candidate import (
    APPROVED_PRIVATE_NETWORK_MARKERS,
    PREFLIGHT_MODE,
    PRIVATE_NETWORK_MARKER,
    RAILWAY_PRIVATE_NETWORK_MARKER,
    RENDER_PRIVATE_NETWORK_MARKER,
    PreflightCandidateSettings,
    PreflightConfigurationError,
)


def _settings(network: str) -> PreflightCandidateSettings:
    return PreflightCandidateSettings(
        database_url="postgresql://synthetic.invalid/preflight",
        bearer_token="synthetic-preflight-token",
        workspace_id="kgm-preflight-workspace",
        project_id="kgm-preflight-project",
        mode=PREFLIGHT_MODE,
        database_network=network,
    )


def test_railway_private_marker_is_explicitly_approved_and_truthful():
    settings = _settings(RAILWAY_PRIVATE_NETWORK_MARKER)
    assert RAILWAY_PRIVATE_NETWORK_MARKER == "railway_private"
    assert RAILWAY_PRIVATE_NETWORK_MARKER in APPROVED_PRIVATE_NETWORK_MARKERS
    assert settings.database_network == "railway_private"
    assert settings.safe_metadata["database_network"] == "railway_private"


def test_historical_render_private_marker_remains_backward_compatible():
    settings = _settings(RENDER_PRIVATE_NETWORK_MARKER)
    assert RENDER_PRIVATE_NETWORK_MARKER == "render_private"
    assert PRIVATE_NETWORK_MARKER == RENDER_PRIVATE_NETWORK_MARKER
    assert RENDER_PRIVATE_NETWORK_MARKER in APPROVED_PRIVATE_NETWORK_MARKERS
    assert settings.safe_metadata["database_network"] == "render_private"


def test_public_or_unknown_network_markers_remain_fail_closed():
    for marker in ("public", "railway_public", "unknown_provider", ""):
        with pytest.raises(PreflightConfigurationError):
            _settings(marker)


def test_private_marker_allowlist_is_bounded_to_observed_provider_contracts():
    assert APPROVED_PRIVATE_NETWORK_MARKERS == frozenset(
        {"render_private", "railway_private"}
    )
