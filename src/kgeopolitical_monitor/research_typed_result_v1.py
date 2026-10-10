"""Fail-closed typed synthetic research result validation (no provider calls)."""
from __future__ import annotations
from .research_request_v1 import validate_request, historically_available, _utc

TYPES = {"CLAIM_EVENT", "CLAIM_CORRECTION", "FORECAST_VERSION", "SOURCE_HEALTH"}
VERIFICATION = {"VERIFIED", "DISPUTED", "UNVERIFIED", "NOT_APPLICABLE"}


def validate_typed_result(request, result):
    validate_request(request)
    base = {"schema_version", "request_id", "consumer_id", "result_id",
            "generated_at_utc", "producer_snapshot_id", "policy_version",
            "research_status", "coverage", "source_health", "records"}
    if not isinstance(result, dict):
        raise ValueError("unapproved result fields")
    version=result.get("schema_version")
    expected=(base if version=="kgm.research.result.v1" else\n              (base | {"corroboration"} if version=="kgm.research.result.v2" else\n               (base | {"corroboration","source_contributions","completeness_semantics"}\n                if version=="kgm.research.result.v3" else set())))
    if not expected or set(result) != expected:
        raise ValueError("unapproved result fields")
    if (result["request_id"], result["consumer_id"], result["policy_version"]) != (
        request["request_id"], request["consumer_id"], request["policy_version"]):
        raise ValueError("result correlation mismatch")
    _utc(result["generated_at_utc"])
    if not isinstance(result["result_id"], str) or not result["result_id"] or not isinstance(result["producer_snapshot_id"], str) or not result["producer_snapshot_id"]:
        raise ValueError("missing result identity")
    if result["research_status"] not in {"COMPLETE", "PARTIAL", "FAILED"}:
        raise ValueError("invalid result status")
    if result["coverage"] not in {"COMPLETE", "PARTIAL", "UNMEASURED"} or result["source_health"] not in {"HEALTHY", "DEGRADED", "STALE", "UNAVAILABLE", "UNMEASURED"}:
        raise ValueError("invalid coverage/health")
    if result["research_status"] == "COMPLETE" and (result["coverage"] != "COMPLETE" or result["source_health"] != "HEALTHY"):
        raise ValueError("false completeness")
    records = result["records"]
    if not isinstance(records, list) or len(records) > request["max_results"]:
        raise ValueError("unbounded records")
    record_fields = {"record_id", "kind", "summary", "verification", "evidence",
                     "contradictions", "revision_of", "forecast"}
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != record_fields:
            raise ValueError("unapproved record fields")
        rid = record["record_id"]
        if not isinstance(rid, str) or not 1 <= len(rid) <= 128 or rid in seen:
            raise ValueError("invalid/duplicate record ID")
        seen.add(rid)
        if record["kind"] not in TYPES or record["verification"] not in VERIFICATION:
            raise ValueError("invalid typed record")
        if not isinstance(record["summary"], str) or not 1 <= len(record["summary"]) <= 1000:
            raise ValueError("invalid summary")
        evidence = record["evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 20:
            raise ValueError("evidence required; no unsupported claims")
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {"source_id", "public_url", "published_at_utc", "available_at_utc"}:
                raise ValueError("invalid evidence provenance")
            if not isinstance(item["source_id"], str) or not item["source_id"] or not isinstance(item["public_url"], str) or not item["public_url"].startswith("https://") or len(item["public_url"]) > 2048:
                raise ValueError("invalid public evidence reference")
            _utc(item["published_at_utc"])
            _utc(item["available_at_utc"])
            if request["mode"] == "HISTORICAL_AS_OF" and not historically_available(item, request["as_of_utc"]):
                raise ValueError("historical evidence lookahead")
        if not isinstance(record["contradictions"], list) or len(record["contradictions"]) > 20 or any(not isinstance(x, str) or len(x) > 128 for x in record["contradictions"]):
            raise ValueError("invalid contradictions")
        if record["revision_of"] is not None and (not isinstance(record["revision_of"], str) or len(record["revision_of"]) > 128):
            raise ValueError("invalid revision lineage")
        forecast = record["forecast"]
        if record["kind"] == "FORECAST_VERSION":
            if not isinstance(forecast, dict) or set(forecast) != {"assumptions", "scenario", "uncertainty"} or any(not isinstance(forecast[x], str) or not 1 <= len(forecast[x]) <= 1000 for x in forecast):
                raise ValueError("untyped forecast")
        elif forecast is not None:
            raise ValueError("forecast attached to factual claim")
    if version in {"kgm.research.result.v2","kgm.research.result.v3"}:
        report=result["corroboration"]
        if not isinstance(report,list) or len(report)>100:
            raise ValueError("invalid corroboration report")
        fields={"corroboration_id","members","source_ids",
                "max_delta_seconds","max_distance_km","claim_relation",
                "origin_assessment","origin_groups","independent_origin_credit",
                "ambiguous","factual_verification_credit",
                "verification_eligibility","verification_blockers","automatic_verification"}
        member_fields={"source_id","observation_id","origin_group","claim_signature"}
        seen_ids=set()
        for item in report:
            if not isinstance(item,dict) or set(item)!=fields:
                raise ValueError("invalid corroboration item")
            cid=item["corroboration_id"]
            if not isinstance(cid,str) or not cid or cid in seen_ids:
                raise ValueError("invalid/duplicate corroboration group")
            seen_ids.add(cid)
            if not isinstance(item["members"],list) or len(item["members"])<2 or len(item["members"])>100:
                raise ValueError("invalid corroboration members")
            for member in item["members"]:
                if not isinstance(member,dict) or set(member)!=member_fields:
                    raise ValueError("invalid corroboration member")
                for field in ("source_id","observation_id"):
                    if not isinstance(member[field],str) or not member[field]:
                        raise ValueError("invalid corroboration member identity")
                for field in ("origin_group","claim_signature"):
                    if member[field] is not None and (not isinstance(member[field],str) or not member[field]):
                        raise ValueError("invalid corroboration member metadata")
            if not isinstance(item["source_ids"],list) or len(item["source_ids"])<2 or any(not isinstance(x,str) or not x for x in item["source_ids"]):
                raise ValueError("invalid corroboration source ids")
            if item["claim_relation"] not in {"AGREES","DIFFERS","UNKNOWN"}:
                raise ValueError("invalid claim relation")
            if item["origin_assessment"] not in {"UNKNOWN","SAME_ORIGIN","DISTINCT_ORIGIN"}:
                raise ValueError("invalid origin assessment")
            if not isinstance(item["origin_groups"],list) or any(not isinstance(x,str) or not x for x in item["origin_groups"]):
                raise ValueError("invalid corroboration origin groups")
            if type(item["independent_origin_credit"]) is not bool or type(item["ambiguous"]) is not bool:
                raise ValueError("invalid corroboration flags")
            if item["factual_verification_credit"] is not False or item["automatic_verification"] is not False:
                raise ValueError("corroboration cannot auto-verify")
            if item["verification_eligibility"] not in {"ELIGIBLE_FOR_EXPLICIT_VERIFICATION","INELIGIBLE","EVENT_CORROBORATED_CLAIM_UNRESOLVED"}:
                raise ValueError("invalid verification eligibility")
            if not isinstance(item["verification_blockers"],list) or any(not isinstance(x,str) or not x for x in item["verification_blockers"]):
                raise ValueError("invalid verification blockers")
            if item["verification_eligibility"]=="ELIGIBLE_FOR_EXPLICIT_VERIFICATION" and item["verification_blockers"]:
                raise ValueError("eligible corroboration has blockers")
            if item["ambiguous"] and item["independent_origin_credit"]:
                raise ValueError("ambiguous corroboration credit denied")
            if item["origin_assessment"]!="DISTINCT_ORIGIN" and item["independent_origin_credit"]:
                raise ValueError("invalid independent-origin credit")
            for field in ("max_delta_seconds","max_distance_km"):
                if not isinstance(item[field],(int,float)) or isinstance(item[field],bool) or item[field]<0:
                    raise ValueError("invalid corroboration metric")

    if version=="kgm.research.result.v3":
        contributions=result["source_contributions"]
        if not isinstance(contributions,list) or not 1<=len(contributions)<=100:
            raise ValueError("invalid source contributions")
        fields={"source_id","required","run_status","observation_count",
                "evidence_observation_count","corroboration_group_count",
                "contribution_status"}
        seen_sources=set()
        for item in contributions:
            if not isinstance(item,dict) or set(item)!=fields:
                raise ValueError("invalid source contribution item")
            sid=item["source_id"]
            if not isinstance(sid,str) or not sid or sid in seen_sources:
                raise ValueError("invalid/duplicate source contribution")
            seen_sources.add(sid)
            if type(item["required"]) is not bool:
                raise ValueError("invalid source contribution requirement")
            if item["run_status"] not in {"OBSERVED","EMPTY","DEGRADED"}:
                raise ValueError("invalid source run contribution status")
            if item["contribution_status"] not in {"CONTRIBUTED","EMPTY","DEGRADED"}:
                raise ValueError("invalid contribution status")
            for field in ("observation_count","evidence_observation_count","corroboration_group_count"):
                if type(item[field]) is not int or item[field]<0:
                    raise ValueError("invalid source contribution count")
            if item["evidence_observation_count"]>item["observation_count"]:
                raise ValueError("invalid source evidence count")
            if item["run_status"]=="EMPTY" and item["contribution_status"]!="EMPTY":
                raise ValueError("empty run contribution mismatch")
            if item["run_status"]=="DEGRADED" and item["contribution_status"]!="DEGRADED":
                raise ValueError("degraded run contribution mismatch")
        semantics=result["completeness_semantics"]
        sf={"semantics_version","portfolio_execution_complete",
            "all_required_sources_invoked","all_required_sources_healthy",
            "all_required_sources_contributed","required_source_empty_present",
            "complete_does_not_imply_all_sources_contributed"}
        if not isinstance(semantics,dict) or set(semantics)!=sf:
            raise ValueError("invalid completeness semantics")
        if semantics["semantics_version"]!="kgm.completeness.v2":
            raise ValueError("invalid completeness semantics version")
        for field in sf-{"semantics_version"}:
            if type(semantics[field]) is not bool:
                raise ValueError("invalid completeness semantics flag")
        if semantics["portfolio_execution_complete"] != (result["research_status"]=="COMPLETE"):
            raise ValueError("completeness semantics/status mismatch")
        if semantics["complete_does_not_imply_all_sources_contributed"] is not True:
            raise ValueError("completeness semantic guardrail missing")
        required=[x for x in contributions if x["required"]]
        expected_invoked=bool(required)
        expected_healthy=all(x["run_status"] in {"OBSERVED","EMPTY"} for x in required)
        expected_contributed=all(x["contribution_status"]=="CONTRIBUTED" for x in required)
        expected_empty=any(x["contribution_status"]=="EMPTY" for x in required)
        if semantics["all_required_sources_invoked"]!=expected_invoked:
            raise ValueError("required source invocation semantics mismatch")
        if semantics["all_required_sources_healthy"]!=expected_healthy:
            raise ValueError("required source health semantics mismatch")
        if semantics["all_required_sources_contributed"]!=expected_contributed:
            raise ValueError("required source contribution semantics mismatch")
        if semantics["required_source_empty_present"]!=expected_empty:
            raise ValueError("required source empty semantics mismatch")
    return result
