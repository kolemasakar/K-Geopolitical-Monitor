from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

POLICY_PATH = Path("docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json")
PROVENANCE_PATH = Path("docs/evidence/P21_1_SOURCE_PROVENANCE_RESOLUTION_2026-09-16.json")
PRE_BASELINE_PATH = Path("docs/evidence/P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_2026-09-16.json")
ONBOARDING_PATH = Path("docs/evidence/P21_5_WAVE_A_ONBOARDING_2026-09-17.json")
HEALTH_PATH = Path("docs/evidence/P21_5_WAVE_A_FRESH_HEALTH_2026-09-17.json")


def _load(root: Path, relative: Path) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _policy_cell_for_source(policy: dict, source: dict) -> dict:
    geographies = source.get("geography_scope") or []
    languages = source.get("language_scope") or []
    if len(geographies) != 1 or len(languages) != 1:
        raise ValueError(f"P21.6 exact cohort requires one geography/language: {source['source_id']}")

    matches = [
        cell
        for cell in policy["target_cells"]
        if cell["geography_scope"] == geographies[0]
        and cell["language"] == languages[0]
        and cell["source_type"] == source["source_type"]
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one approved policy cell for {source['source_id']}, got {len(matches)}"
        )
    return matches[0]


def _confirmed_source_level_origin_group(source: dict) -> str | None:
    if (
        source.get("origin_group_id")
        and source.get("provenance_completeness") == "KNOWN"
        and source.get("syndication_or_copy_relation") == "ORIGINAL"
    ):
        return str(source["origin_group_id"])
    return None


def _is_healthy_fresh(source: dict, health: dict) -> bool:
    health_ok = health.get("status") == "SUCCESS"
    age = health.get("content_age_minutes")
    freshness = source.get("expected_freshness_minutes")
    measured_fresh = (
        health_ok
        and isinstance(age, (int, float))
        and isinstance(freshness, (int, float))
        and age <= freshness
    )
    declared = source.get("p21_5_health_snapshot")

    if declared == "HEALTHY_FRESH" and not measured_fresh:
        raise ValueError(f"Inconsistent HEALTHY_FRESH evidence for {source['source_id']}")
    if declared == "HEALTHY_COLLECTOR_STALE_CONTENT" and measured_fresh:
        raise ValueError(f"Inconsistent stale-content evidence for {source['source_id']}")
    return measured_fresh


def _evaluate_status(post: dict, policy_cell: dict) -> tuple[str, list[str]]:
    thresholds = policy_cell["thresholds"]
    count = post["governed_source_count"]
    healthy = post["healthy_source_count"]
    independent_lb = post["known_independent_origin_lower_bound"]
    stale_share = post["stale_or_failed_share"]
    dominant_upper = post["dominant_origin_share_upper_bound"]

    if count == 0:
        if policy_cell["requirement_state"] == "REQUIRED":
            return "MISSING_EXPECTED_COVERAGE", ["NO_MATCHING_GOVERNED_SOURCE"]
        return "THIN", ["NO_MATCHING_GOVERNED_SOURCE"]

    if healthy < thresholds["minimum_healthy_source_count"] or (
        stale_share is not None and stale_share > thresholds["maximum_stale_share"]
    ):
        return "DEGRADED_COLLECTION", ["HEALTH_OR_FRESHNESS_THRESHOLD_NOT_MET"]

    reasons: list[str] = []
    if count < thresholds["minimum_source_count"]:
        reasons.append("SOURCE_COUNT_BELOW_MINIMUM")
    if independent_lb < thresholds["minimum_independent_origin_count"]:
        reasons.append("INDEPENDENT_ORIGIN_LOWER_BOUND_BELOW_MINIMUM")
    if (
        dominant_upper is not None
        and dominant_upper > thresholds["maximum_dominant_origin_share"]
    ):
        reasons.append("DOMINANT_ORIGIN_SHARE_UPPER_BOUND_ABOVE_MAXIMUM")

    if reasons:
        return "THIN", reasons
    return "ADEQUATE", ["ALL_POLICY_THRESHOLDS_SATISFIED_FAIL_CLOSED"]


def _overlay_cell(pre: dict, policy_cell: dict, additions: list[tuple[dict, dict]]) -> dict:
    post = copy.deepcopy(pre)
    governed = set(pre["governed_source_ids"])
    healthy = set(pre["healthy_source_ids"])
    stale = set(pre["stale_or_failed_source_ids"])
    unresolved = set(pre["unresolved_origin_source_ids"])
    known_origins = set(pre["known_origin_groups"])

    for source, health_evidence in additions:
        source_id = source["source_id"]
        governed.add(source_id)

        origin_group = _confirmed_source_level_origin_group(source)
        if origin_group is None:
            unresolved.add(source_id)
        else:
            known_origins.add(origin_group)
            unresolved.discard(source_id)

        if _is_healthy_fresh(source, health_evidence):
            healthy.add(source_id)
            stale.discard(source_id)
        else:
            stale.add(source_id)
            healthy.discard(source_id)

    post["governed_source_ids"] = sorted(governed)
    post["governed_source_count"] = len(governed)
    post["known_origin_groups"] = sorted(known_origins)
    post["known_independent_origin_lower_bound"] = len(known_origins)
    post["unresolved_origin_source_ids"] = sorted(unresolved)
    post["healthy_source_ids"] = sorted(healthy)
    post["healthy_source_count"] = len(healthy)
    post["stale_or_failed_source_ids"] = sorted(stale)
    post["stale_or_failed_share"] = len(stale) / len(governed) if governed else None

    # Fail-closed: unresolved streams could all share one underlying origin.
    if not governed:
        post["dominant_origin_share_upper_bound"] = None
    elif unresolved:
        post["dominant_origin_share_upper_bound"] = min(
            1.0, (len(unresolved) + (1 if known_origins else 0)) / len(governed)
        )
    else:
        post["dominant_origin_share_upper_bound"] = 1.0 / len(known_origins)

    status, reasons = _evaluate_status(post, policy_cell)
    post["status"] = status
    post["reason_codes"] = reasons
    return post


def build_report(root: Path) -> dict:
    policy = _load(root, POLICY_PATH)
    provenance = _load(root, PROVENANCE_PATH)
    pre_baseline = _load(root, PRE_BASELINE_PATH)
    onboarding = _load(root, ONBOARDING_PATH)
    health = _load(root, HEALTH_PATH)

    if pre_baseline["principles"]["verification_authority"] != "P13.5/P13.6":
        raise ValueError("P21.6 cannot change factual-verification authority")

    active_sources = [
        source
        for source in onboarding["sources"]
        if source.get("p21_5_repository_activation") == "ACTIVE"
    ]
    if not active_sources:
        raise ValueError("No P21.5 repository-active sources found")

    health_by_source = {item["source_id"]: item for item in health["sources"]}
    pre_by_cell = {cell["cell_id"]: cell for cell in pre_baseline["cells"]}

    additions_by_cell: dict[str, list[tuple[dict, dict]]] = {}
    policy_by_cell: dict[str, dict] = {}
    for source in active_sources:
        source_id = source["source_id"]
        if source_id not in health_by_source:
            raise ValueError(f"Missing P21.5 health evidence for {source_id}")
        policy_cell = _policy_cell_for_source(policy, source)
        cell_id = policy_cell["cell_id"]
        if cell_id not in pre_by_cell:
            raise ValueError(f"P21.3 pre-baseline missing target cell {cell_id}")
        policy_by_cell[cell_id] = policy_cell
        additions_by_cell.setdefault(cell_id, []).append((source, health_by_source[source_id]))

    cohort_ids = sorted(additions_by_cell)
    cell_effects: list[dict] = []
    for cell_id in cohort_ids:
        pre = pre_by_cell[cell_id]
        post = _overlay_cell(pre, policy_by_cell[cell_id], additions_by_cell[cell_id])
        cell_effects.append(
            {
                "cell_id": cell_id,
                "requirement_state": pre["requirement_state"],
                "criticality": pre["criticality"],
                "pre": {
                    "status": pre["status"],
                    "governed_source_ids": pre["governed_source_ids"],
                    "governed_source_count": pre["governed_source_count"],
                    "healthy_fresh_source_ids": pre["healthy_source_ids"],
                    "healthy_fresh_source_count": pre["healthy_source_count"],
                    "known_origin_groups": pre["known_origin_groups"],
                    "confirmed_independent_origin_lower_bound": pre[
                        "known_independent_origin_lower_bound"
                    ],
                    "reason_codes": pre["reason_codes"],
                },
                "post": {
                    "status": post["status"],
                    "governed_source_ids": post["governed_source_ids"],
                    "governed_source_count": post["governed_source_count"],
                    "healthy_fresh_source_ids": post["healthy_source_ids"],
                    "healthy_fresh_source_count": post["healthy_source_count"],
                    "known_origin_groups": post["known_origin_groups"],
                    "confirmed_independent_origin_lower_bound": post[
                        "known_independent_origin_lower_bound"
                    ],
                    "stale_or_failed_source_ids": post["stale_or_failed_source_ids"],
                    "stale_or_failed_share": post["stale_or_failed_share"],
                    "dominant_origin_share_upper_bound": post[
                        "dominant_origin_share_upper_bound"
                    ],
                    "reason_codes": post["reason_codes"],
                },
            }
        )

    pre_status = Counter(item["pre"]["status"] for item in cell_effects)
    post_status = Counter(item["post"]["status"] for item in cell_effects)

    governed_delta = sum(
        item["post"]["governed_source_count"] - item["pre"]["governed_source_count"]
        for item in cell_effects
    )
    healthy_delta = sum(
        item["post"]["healthy_fresh_source_count"] - item["pre"]["healthy_fresh_source_count"]
        for item in cell_effects
    )
    origin_delta = sum(
        item["post"]["confirmed_independent_origin_lower_bound"]
        - item["pre"]["confirmed_independent_origin_lower_bound"]
        for item in cell_effects
    )
    adequate_delta = post_status["ADEQUATE"] - pre_status["ADEQUATE"]
    pre_required_missing = sum(
        1
        for item in cell_effects
        if item["requirement_state"] == "REQUIRED"
        and item["pre"]["status"] == "MISSING_EXPECTED_COVERAGE"
    )
    post_required_missing = sum(
        1
        for item in cell_effects
        if item["requirement_state"] == "REQUIRED"
        and item["post"]["status"] == "MISSING_EXPECTED_COVERAGE"
    )

    portfolio_pre = Counter(pre_baseline["global_summary"]["status_counts"])
    portfolio_post = portfolio_pre.copy()
    for item in cell_effects:
        portfolio_post[item["pre"]["status"]] -= 1
        portfolio_post[item["post"]["status"]] += 1

    automatic_claim_independence_credit_delta = sum(
        1 for source in active_sources if source.get("independence_credit_granted") is True
    )

    return {
        "schema_version": "kgm.p21.6.intelligence_quality_impact.v1",
        "assessed_at": health["assessed_at"],
        "inputs": {
            "approved_policy_manifest": str(POLICY_PATH),
            "pre_operational_adequacy_baseline": str(PRE_BASELINE_PATH),
            "pre_source_provenance": str(PROVENANCE_PATH),
            "wave_a_onboarding": str(ONBOARDING_PATH),
            "wave_a_fresh_health": str(HEALTH_PATH),
        },
        "cohort": {
            "basis": "EXACT_P21_5_WAVE_A_REPOSITORY_ACTIVE_POLICY_CELLS",
            "cell_ids": cohort_ids,
            "source_ids": sorted(source["source_id"] for source in active_sources),
            "cell_count": len(cohort_ids),
            "source_count": len(active_sources),
        },
        "summary": {
            "governed_source_path_delta": governed_delta,
            "healthy_fresh_source_path_delta": healthy_delta,
            "confirmed_independent_origin_lower_bound_delta": origin_delta,
            "automatic_factual_independence_credit_delta": automatic_claim_independence_credit_delta,
            "pre_status_counts": dict(sorted(pre_status.items())),
            "post_status_counts": dict(sorted(post_status.items())),
            "adequate_cell_delta": adequate_delta,
            "missing_required_cell_delta": post_required_missing - pre_required_missing,
            "portfolio_pre_status_counts": dict(sorted(portfolio_pre.items())),
            "portfolio_post_structural_status_counts": {
                key: value for key, value in sorted(portfolio_post.items()) if value
            },
        },
        "cells": cell_effects,
        "downstream_intelligence_quality": {
            "semantic_post_wave_a_corpus_observed": False,
            "verification_yield_impact": "NOT_OBSERVED",
            "contradiction_workload_impact": "NOT_OBSERVED",
            "forecast_input_impact": "NOT_OBSERVED",
            "reason": (
                "No deployed post-Wave-A semantic corpus is available. Structural coverage, "
                "source-health and source-topology changes cannot be promoted into factual-"
                "verification, contradiction-workload or forecast-input claims."
            ),
        },
        "principles": {
            "verification_authority": "P13.5/P13.6",
            "coverage_health_is_not_truth": True,
            "source_level_origin_group_is_topology_evidence_not_claim_truth": True,
            "automatic_independence_credit_from_wave_a": False,
            "exact_cohort_only": True,
            "no_counterfactual_semantic_quality_claim": True,
        },
        "safety_boundary": {
            "deployed_runtime_mutated": False,
            "service_restart": False,
            "runtime_deployment": False,
            "production_live": False,
            "paid_or_shared_resources_authorized": False,
            "migration_033": "NOT_CREATED / NOT_PREAUTHORIZED",
            "plugin_build": False,
            "plugin_publication": False,
            "future_source_waves_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic P21.6 intelligence-quality impact evidence.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report(args.root)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else args.root / args.output
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
