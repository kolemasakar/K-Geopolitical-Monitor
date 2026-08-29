"""Server-rendered owner/admin dashboard for persisted project-local state.

The renderer is intentionally static and script-free. All dynamic values are HTML
escaped so persisted source/report text cannot become executable markup.
"""

from html import escape


DASHBOARD_SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
    "Content-Security-Policy": (
        "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; "
        "form-action 'none'; frame-ancestors 'none'"
    ),
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _items(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _plain(value: object) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def _text(value: object) -> str:
    return escape(_plain(value), quote=True)


def _percent(value: object) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return _plain(value)


def _table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    if not rows:
        return '<p class="empty">No persisted records available.</p>'
    head = "".join(f"<th>{escape(label)}</th>" for label in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_text(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _scenario_summary(value: object) -> str:
    scenarios = _items(value)
    if not scenarios:
        return "—"
    rendered: list[str] = []
    for scenario in scenarios:
        label = _plain(scenario.get("label") or scenario.get("scenario_type"))
        probability = _percent(scenario.get("calibrated_probability"))
        rendered.append(f"{label}: {probability}")
    return "; ".join(rendered)


def render_admin_dashboard(snapshot: dict[str, object]) -> str:
    """Render one read-only dashboard view from an already-read snapshot."""

    system = _mapping(snapshot.get("system"))
    summary = _mapping(system.get("state_summary"))
    last_cycle = _mapping(summary.get("last_monitoring_cycle"))
    errors = _items(system.get("current_errors"))

    error_rows = [
        (
            item.get("kind"),
            item.get("identifier"),
            item.get("status"),
            item.get("error"),
            item.get("observed_at"),
        )
        for item in errors
    ]

    watch_rows = [
        (
            item.get("watch_id"),
            item.get("name"),
            item.get("state"),
            item.get("due"),
            item.get("running"),
            item.get("failed"),
            item.get("cadence_minutes"),
            item.get("next_due_at"),
            item.get("latest_run_id"),
        )
        for item in _items(snapshot.get("watches"))
    ]

    source_rows = [
        (
            item.get("source_id"),
            item.get("source_name"),
            item.get("source_status") or "NOT_ASSESSED",
            item.get("reliability_rating") or item.get("legacy_reliability"),
            item.get("availability_state"),
            item.get("last_attempt_at"),
            item.get("last_attempt_error"),
        )
        for item in _items(snapshot.get("sources"))
    ]

    coverage_rows = [
        (
            item.get("scope_key"),
            _percent(item.get("coverage_ratio")),
            _percent(item.get("coverage_confidence")),
            item.get("gap_count"),
            item.get("unavailable_count"),
            item.get("stale_count"),
            item.get("unknown_count"),
            item.get("unmeasured_count"),
            item.get("assessed_at"),
        )
        for item in _items(snapshot.get("coverage"))
    ]

    finding_rows = [
        (
            item.get("finding_id"),
            item.get("title"),
            _percent(item.get("importance_score")),
            _percent(item.get("finding_confidence")),
            item.get("verification_state") or "NOT_AVAILABLE",
            item.get("created_at"),
        )
        for item in _items(snapshot.get("findings"))
    ]

    alert_rows = [
        (
            item.get("alert_id"),
            item.get("event"),
            item.get("priority"),
            item.get("status"),
            item.get("verification_state") or "NOT_AVAILABLE",
            _percent(item.get("importance_score")),
            item.get("last_updated_at"),
        )
        for item in _items(snapshot.get("alerts"))
    ]

    forecast_rows = [
        (
            item.get("forecast_id"),
            item.get("question"),
            item.get("horizon"),
            item.get("status"),
            item.get("evaluation_deadline"),
            item.get("version_number"),
            _scenario_summary(item.get("scenarios")),
        )
        for item in _items(snapshot.get("forecasts"))
    ]

    attempt_rows = [
        (
            item.get("attempted_at"),
            item.get("source_id"),
            item.get("source_name"),
            item.get("status"),
            item.get("item_count"),
            item.get("error"),
        )
        for item in _items(snapshot.get("collection_attempts"))
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>K-Geopolitical Monitor Admin Dashboard</title>
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ margin: 0; padding: 1.25rem; max-width: 1500px; margin-inline: auto; }}
h1 {{ margin-bottom: .25rem; }}
h2 {{ margin-top: 2rem; border-bottom: 1px solid #8886; padding-bottom: .35rem; }}
.meta {{ opacity: .78; margin-top: 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .75rem; }}
.card {{ border: 1px solid #8886; border-radius: .6rem; padding: .8rem; }}
.card strong {{ display: block; font-size: .82rem; opacity: .75; margin-bottom: .3rem; }}
.notice {{ border-left: .3rem solid currentColor; padding: .65rem .85rem; background: #8881; }}
.table-wrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: .9rem; }}
th, td {{ border-bottom: 1px solid #8885; text-align: left; vertical-align: top; padding: .48rem .55rem; }}
th {{ position: sticky; top: 0; background: Canvas; }}
.empty {{ opacity: .7; font-style: italic; }}
footer {{ margin-top: 2.5rem; font-size: .85rem; opacity: .75; }}
</style>
</head>
<body>
<header>
<h1>K-Geopolitical Monitor — Admin Read-Only Dashboard</h1>
<p class="meta">Generated: {_text(snapshot.get("generated_at"))} · Contract: {_text(snapshot.get("dashboard_contract_version"))}</p>
<p class="notice">Read-only persisted-state view. Coverage confidence measures assessment observability, not claim verification. Forecast probability is analytical, not factual confidence. Dashboard wording never strengthens evidence.</p>
</header>

<section>
<h2>System</h2>
<div class="grid">
<div class="card"><strong>Runtime storage</strong>{_text(system.get("runtime_storage"))}</div>
<div class="card"><strong>Production/live</strong>{_text(system.get("production_live"))}</div>
<div class="card"><strong>System uptime</strong>{_text(system.get("system_uptime_instrumentation"))}</div>
<div class="card"><strong>Active watches</strong>{_text(summary.get("active_monitoring_watches"))}</div>
<div class="card"><strong>Last cycle</strong>{_text(last_cycle.get("status"))} · {_text(last_cycle.get("completed_at") or last_cycle.get("started_at"))}</div>
<div class="card"><strong>Current errors</strong>{_text(system.get("current_error_count"))}</div>
</div>
{_table(("Kind", "Identifier", "Status", "Error", "Observed"), error_rows)}
</section>

<section>
<h2>Monitoring watches</h2>
{_table(("Watch", "Name", "State", "Due", "Running", "Failed", "Cadence min", "Next due", "Latest run"), watch_rows)}
</section>

<section>
<h2>Source state</h2>
{_table(("Source", "Name", "Reputation status", "Reliability", "Availability", "Latest attempt", "Error"), source_rows)}
</section>

<section>
<h2>Coverage</h2>
{_table(("Scope", "Coverage ratio", "Coverage confidence", "GAP", "Unavailable", "Stale", "Unknown", "Unmeasured", "Assessed"), coverage_rows)}
</section>

<section>
<h2>Recent findings</h2>
{_table(("Finding", "Title", "Importance", "Finding confidence", "Verification", "Created"), finding_rows)}
</section>

<section>
<h2>Recent alerts</h2>
{_table(("Alert", "Event", "Priority", "Status", "Verification", "Importance", "Updated"), alert_rows)}
</section>

<section>
<h2>Active forecasts</h2>
{_table(("Forecast", "Question", "Horizon", "Status", "Deadline", "Version", "Calibrated scenario probabilities"), forecast_rows)}
</section>

<section>
<h2>Recent source collection attempts</h2>
{_table(("Attempted", "Source", "Name", "Status", "Items", "Error"), attempt_rows)}
</section>

<footer>Owner/admin-only read-only surface. No public-web substitution for unavailable persisted backend state.</footer>
</body>
</html>"""
